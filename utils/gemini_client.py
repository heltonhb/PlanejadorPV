"""
Cliente centralizado para comunicação com a API Gemini.

Fornece:
- Retry automático com backoff exponencial
- Cache de respostas para reduzir custos
- Tratamento de erros padronizado
- Validação de entrada
"""

import hashlib
import logging
import os
import threading
import time
from collections import OrderedDict
from typing import Optional

from google import genai

logger = logging.getLogger(__name__)

# Configurações
# gemini-2.0-flash: free tier = 30 RPM (1 req a cada 2s)
# gemini-2.5-flash: free tier = 10 RPM (1 req a cada 6s) — maior qualidade
MODELO_PADRAO = "gemini-2.5-flash"
MAX_RETRIES = 3
BACKOFF_BASE = 2  # segundos
CACHE_SIZE = 256  # número de entradas no cache LRU

# Rate limiter global — proativo para evitar 429
# Usamos 7s para ficar abaixo do limite de 10 RPM do gemini-2.5-flash free tier
MIN_INTERVALO_REQ = 7  # segundos entre requisições


class GeminiError(Exception):
    """Erro base para falhas do Gemini."""
    
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(message)


class GeminiAPIKeyError(GeminiError):
    """Chave de API inválida ou não configurada."""
    
    def __init__(self, message: str = "GEMINI_API_KEY não configurada ou inválida."):
        super().__init__(message, code="API_KEY_INVALID")


class GeminiQuotaError(GeminiError):
    """Limite de requisições excedido."""
    
    def __init__(self, message: str = "Limite de requisições excedido. Aguarde e tente novamente."):
        super().__init__(message, code="QUOTA_EXCEEDED")


class GeminiSafetyError(GeminiError):
    """Conteúdo bloqueado pelos filtros de segurança."""
    
    def __init__(self, message: str = "Conteúdo bloqueado pelos filtros de segurança."):
        super().__init__(message, code="SAFETY_BLOCK")


class GeminiServerError(GeminiError):
    """Erro interno do servidor."""
    
    def __init__(self, message: str = "Servidor do Gemini temporariamente indisponível."):
        super().__init__(message, code="SERVER_ERROR")


def _get_gemini_key() -> Optional[str]:
    """
    Obtém a chave da API Gemini de variáveis de ambiente ou secrets do Streamlit.
    
    Returns:
        A chave da API ou None se não encontrada.
    """
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    
    return None


def _gerar_cache_key(modelo: str, conteudo: str) -> str:
    """Gera uma chave de cache baseada no modelo e conteúdo."""
    dados = f"{modelo}:{conteudo}"
    return hashlib.sha256(dados.encode()).hexdigest()[:32]


# ── Rate limiter thread-safe ──
_ultima_req: float = 0.0
_rate_lock = threading.Lock()


def _aguardar_rate_limit():
    """Aguarda o intervalo mínimo entre requisições (rate limiter proativo)."""
    global _ultima_req
    with _rate_lock:
        agora = time.time()
        desde_ultima = agora - _ultima_req
        if desde_ultima < MIN_INTERVALO_REQ:
            espera = MIN_INTERVALO_REQ - desde_ultima
            logger.info(f"⏳ Rate limiter: aguardando {espera:.1f}s (última req há {desde_ultima:.1f}s)")
            time.sleep(espera)
        _ultima_req = time.time()


class GeminiClient:
    """
    Cliente para comunicação com a API Gemini.
    
    Features:
    - Retry automático com backoff exponencial
    - Cache de respostas em memória com política LRU
    - Rate limiter proativo entre requisições
    - Tratamento de erros estruturado
    - Validação de entrada
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        modelo: str = MODELO_PADRAO,
        max_retries: int = MAX_RETRIES,
        cache_size: int = CACHE_SIZE,
        enable_cache: bool = True,
    ):
        self._api_key = api_key or _get_gemini_key()
        self.modelo = modelo
        self.max_retries = max_retries
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._cache_size = cache_size
        self._enable_cache = enable_cache
        self._client: Optional[genai.Client] = None
    
    @property
    def api_key_configured(self) -> bool:
        """Verifica se a API key está configurada."""
        return bool(self._api_key)
    
    def _get_client(self) -> genai.Client:
        """Obtém ou cria o cliente Gemini."""
        if self._client is None:
            if not self._api_key:
                raise GeminiAPIKeyError()
            self._client = genai.Client(api_key=self._api_key)
        return self._client
    
    def _get_cached(self, cache_key: str) -> Optional[str]:
        """Obtém resposta do cache se disponível."""
        if not self._enable_cache:
            return None
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]
        return None
    
    def _set_cached(self, cache_key: str, value: str):
        """Armazena resposta no cache com política LRU."""
        if not self._enable_cache:
            return
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
        self._cache[cache_key] = value
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)
    
    def _classificar_erro(self, erro: Exception) -> GeminiError:
        """Classifica o erro e retorna exceção apropriada."""
        msg = str(erro).lower()
        
        if "api_key" in msg or "not found" in msg or "invalid" in msg:
            return GeminiAPIKeyError()
        elif "quota" in msg or "rate" in msg or "429" in msg:
            return GeminiQuotaError()
        elif "safety" in msg or "blocked" in msg or "harm" in msg:
            return GeminiSafetyError()
        elif any(code in msg for code in ["500", "503", "server", "internal"]):
            return GeminiServerError()
        else:
            return GeminiError(f"Erro inesperado: {str(erro)[:200]}")
    
    def _executar_com_retry(
        self,
        contents: list,
        generation_config: Optional[dict] = None,
    ) -> str:
        """Executa requisição com retry automático com backoff adaptativo para quotas."""
        client = self._get_client()
        ultimo_erro = None
        
        # Se for erro de quota/limite, permitimos mais tentativas com esperas mais longas
        limite_tentativas = self.max_retries
        
        tentativa = 0
        while tentativa < limite_tentativas:
            try:
                resposta = client.models.generate_content(
                    model=self.modelo,
                    contents=contents,
                    generation_config=generation_config,
                )
                return resposta.text or ""
            
            except Exception as e:
                ultimo_erro = e
                erro_classificado = self._classificar_erro(e)
                
                if isinstance(erro_classificado, (GeminiAPIKeyError, GeminiSafetyError)):
                    raise erro_classificado
                
                # Se detectarmos erro de limite de requisições, aumentamos as tentativas
                # e aplicamos uma espera progressiva maior (backoff exponencial agressivo)
                if isinstance(erro_classificado, GeminiQuotaError):
                    limite_tentativas = max(limite_tentativas, 6)
                    wait_time = 5 * (BACKOFF_BASE ** tentativa)  # 5s, 10s, 20s, 40s, 80s, 160s
                
                if tentativa < limite_tentativas - 1:
                    logger.warning(
                        f"Tentativa {tentativa + 1}/{limite_tentativas} falhou: {e}. "
                        f"Retry em {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    tentativa += 1
                else:
                    break
        
        raise self._classificar_erro(ultimo_erro)
    
    def gerar_texto(
        self,
        prompt: str,
        usar_cache: bool = True,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Gera texto a partir de um prompt."""
        if not self._api_key:
            raise GeminiAPIKeyError()
        
        if not prompt or not prompt.strip():
            return ""
        
        if usar_cache:
            cache_key = _gerar_cache_key(self.modelo, prompt)
            cached = self._get_cached(cache_key)
            if cached:
                logger.debug(f"Cache hit para prompt: {cache_key[:8]}...")
                return cached
        
        generation_config = {
            "temperature": max(0.0, min(1.0, temperatura)),
            "max_output_tokens": max_tokens,
        }
        
        # Rate limiter proativo
        _aguardar_rate_limit()
        
        contents = [prompt]
        resultado = self._executar_com_retry(contents, generation_config)
        
        if usar_cache:
            self._set_cached(cache_key, resultado)
        
        return resultado
    
    def gerar_com_imagem(
        self,
        prompt: str,
        imagem,
        usar_cache: bool = False,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Gera texto a partir de um prompt e uma imagem."""
        if not self._api_key:
            raise GeminiAPIKeyError()
        
        if not prompt or not prompt.strip():
            return ""
        
        generation_config = {
            "temperature": max(0.0, min(1.0, temperatura)),
            "max_output_tokens": max_tokens,
        }
        
        # Rate limiter proativo
        _aguardar_rate_limit()
        
        contents = [prompt, imagem]
        return self._executar_com_retry(contents, generation_config)
    
    def limpar_cache(self):
        """Limpa o cache de respostas."""
        self._cache.clear()
        logger.info("Cache do GeminiClient limpo")


_cliente_global: Optional[GeminiClient] = None


def get_cliente(
    api_key: Optional[str] = None,
    modelo: str = MODELO_PADRAO,
    **kwargs,
) -> GeminiClient:
    """Obtém instância singleton do cliente Gemini."""
    global _cliente_global
    
    if _cliente_global is None or _cliente_global.modelo != modelo:
        _cliente_global = GeminiClient(
            api_key=api_key,
            modelo=modelo,
            **kwargs,
        )
    
    return _cliente_global


def reset_cliente():
    """Reseta a instância global do cliente."""
    global _cliente_global
    if _cliente_global:
        _cliente_global.limpar_cache()
    _cliente_global = None
