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
MODELOS_FALLBACK = [
    "gemini-2.5-flash",   # primeira escolha (melhor qualidade, 10 RPM, 1.500 RPD)
    "gemini-1.5-flash",   # fallback (mais cotas: 30 RPM, 1.500 RPD)
    "gemini-2.0-flash",   # último fallback (30 RPM, cota separada)
]
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
    """Limite de requisições excedido (rate limit por minuto)."""
    
    def __init__(self, message: str = "Limite de requisições excedido. Aguarde alguns minutos e tente novamente."):
        super().__init__(message, code="QUOTA_EXCEEDED")


class GeminiDailyQuotaError(GeminiError):
    """Limite diário de requisições excedido — só resetará no próximo dia."""
    
    def __init__(self, message: str = "Limite diário de requisições excedido. O limite será resetado automaticamente — volte a usar amanhã."):
        super().__init__(message, code="DAILY_QUOTA_EXCEEDED")


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

# Cache de bloqueio por quota diária POR MODELO — evita tentativas em vão por 1h
# Ex: {"gemini-2.5-flash": 1234567890.0}
_quota_blocked: dict[str, float] = {}
_quota_lock = threading.Lock()


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


def _verificar_quota_block(modelo: str):
    """
    Verifica se há bloqueio de quota diária para o modelo especificado.
    """
    with _quota_lock:
        expira = _quota_blocked.get(modelo, 0.0)
        if time.time() < expira:
            raise GeminiDailyQuotaError(
                f"Limite diário excedido para {modelo}. "
                f"Tente outro modelo ou aguarde."
            )


def _ativar_quota_block(modelo: str, tempo_bloqueio: int = 3600):
    """
    Ativa bloqueio de quota diária para um modelo específico.
    """
    with _quota_lock:
        _quota_blocked[modelo] = time.time() + tempo_bloqueio
        logger.warning(f"🔒 Bloqueio de quota diária para {modelo} por {tempo_bloqueio // 60}min")


def _limpar_quota_block(modelo: Optional[str] = None):
    """Limpa bloqueio de quota diária."""
    global _quota_blocked
    with _quota_lock:
        if modelo:
            _quota_blocked.pop(modelo, None)
            logger.info(f"🔓 Bloqueio removido para {modelo}")
        else:
            _quota_blocked.clear()
            logger.info("🔓 Todos os bloqueios de quota removidos")


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
        modelos_fallback: Optional[list[str]] = None,
        max_retries: int = MAX_RETRIES,
        cache_size: int = CACHE_SIZE,
        enable_cache: bool = True,
    ):
        self._api_key = api_key or _get_gemini_key()
        self.modelos = modelos_fallback or MODELOS_FALLBACK
        # Se o modelo passado não estiver na lista, coloca como primeiro
        if modelo and modelo not in self.modelos:
            self.modelos.insert(0, modelo)
        self.modelo_atual_idx = 0
        self.modelo = self.modelos[0]
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
        """Classifica o erro e retorna exceção apropriada.
        
        Tenta diferenciar entre:
        - Cota diária excedida (RPD) → GeminiDailyQuotaError
        - Rate limit por minuto (RPM) → GeminiQuotaError
        - Outros erros → classes específicas
        """
        msg = str(erro).lower()
        
        if "api_key" in msg or "not found" in msg or "invalid" in msg:
            return GeminiAPIKeyError()
        elif "quota" in msg or "429" in msg or "rate limit" in msg or "rate exceeded" in msg or "too many" in msg:
            # Tenta diferenciar diário de rate limit
            if any(w in msg for w in ["per day", "daily", "per_day", "day"]):
                return GeminiDailyQuotaError()
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
        config: Optional[dict] = None,
    ) -> str:
        """Executa requisição com retry automático com backoff adaptativo para quotas.
        
        Lógica:
        - Erros de API key ou safety → propaga imediatamente
        - Erro de cota DIÁRIA detectado → bloqueia 1h e propaga
        - Erro de rate limit (RPM) → até 6 retries com backoff 5s, 10s, 20s, 40s, 80s, 160s
        - Se TODOS os retries falharem com erro de quota → reclassifica como diário
          (pois rate limit por minuto teria sido resolvido em ~5min de espera)
        """
        client = self._get_client()
        ultimo_erro = None
        todas_quota = True  # todas as falhas foram erro de quota?
        
        # Se for erro de quota/limite, permitimos mais tentativas com esperas mais longas
        limite_tentativas = self.max_retries
        
        tentativa = 0
        while tentativa < limite_tentativas:
            try:
                resposta = client.models.generate_content(
                    model=self.modelo,
                    contents=contents,
                    config=config,
                )
                return resposta.text or ""
            
            except Exception as e:
                ultimo_erro = e
                erro_classificado = self._classificar_erro(e)
                
                if isinstance(erro_classificado, (GeminiAPIKeyError, GeminiSafetyError)):
                    raise erro_classificado
                
                # Se for quota DIÁRIA detectada na mensagem, não adianta retry
                if isinstance(erro_classificado, GeminiDailyQuotaError):
                    # Bloquear este modelo específico
                    _ativar_quota_block(self.modelo)
                    
                    # Tentar fallback para próximo modelo
                    if self.modelo_atual_idx < len(self.modelos) - 1:
                        self.modelo_atual_idx += 1
                        self.modelo = self.modelos[self.modelo_atual_idx]
                        logger.warning(
                            "⚠️ Cota diária esgotada em %s. "
                            "Fallback para %s",
                            self.modelos[self.modelo_atual_idx - 1],
                            self.modelo,
                        )
                        # Resetar contadores para o novo modelo
                        tentativa = 0
                        todas_quota = True
                        continue
                    raise erro_classificado
                
                # Se NÃO for erro de quota, marca que nem todos são quota
                if not isinstance(erro_classificado, GeminiQuotaError):
                    todas_quota = False
                    wait_time = BACKOFF_BASE ** tentativa  # 1s, 2s, 4s...
                else:
                    # Rate limit (RPM): algumas tentativas com backoff
                    # Se após 3 tentativas (~35s) ainda falhar, é cota diária
                    limite_tentativas = max(limite_tentativas, 3)
                    wait_time = 5 * (BACKOFF_BASE ** tentativa)  # 5s, 10s, 20s
                
                if tentativa < limite_tentativas - 1:
                    logger.warning(
                        f"Tentativa {tentativa + 1}/{limite_tentativas} falhou: {e}. "
                        f"Retry em {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    tentativa += 1
                else:
                    break
        
        # Se TODAS as tentativas falharam com erro de quota (429) mesmo após ~5min de espera,
        # é quase certeza que é limite DIÁRIO, não rate limit por minuto
        if todas_quota:
            logger.warning(
                "Todas as tentativas falharam com erro de quota mesmo após backoff. "
                "Reclassificando como cota DIÁRIA."
            )
            _ativar_quota_block(self.modelo)
            raise GeminiDailyQuotaError()
        
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
        
        config = {
            "temperature": max(0.0, min(1.0, temperatura)),
            "max_output_tokens": max_tokens,
        }
        
        # Rate limiter proativo
        _aguardar_rate_limit()
        
        contents = [prompt]
        resultado = self._executar_com_retry(contents, config)
        
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
        
        config = {
            "temperature": max(0.0, min(1.0, temperatura)),
            "max_output_tokens": max_tokens,
        }
        
        # Rate limiter proativo
        _aguardar_rate_limit()
        
        contents = [prompt, imagem]
        return self._executar_com_retry(contents, config)
    
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
