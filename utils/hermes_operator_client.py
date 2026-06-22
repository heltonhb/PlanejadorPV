"""
Cliente para o Hermes Operator — API OpenAI-compatível via Hugging Face Space.

Usa OpenRouter como provider, modelo deepseek/deepseek-chat.
Serve como substituto principal do Gemini no sistema.

Configuração necessária no .env ou Streamlit Secrets:
    HERMES_OPERATOR_API_KEY=<sua_chave>
    HERMES_OPERATOR_API_URL=https://heltonhb-hermes-operator.hf.space/v1/chat/completions
    HERMES_OPERATOR_MODEL=deepseek/deepseek-chat
"""

import logging
import os
from typing import Optional

from utils.prompts import PERSONA_RAG

logger = logging.getLogger(__name__)

# Configurações padrão — podem ser sobrescritas via .env ou construtor
API_URL_PADRAO = "https://heltonhb-hermes-operator.hf.space/v1/chat/completions"
MODELO_PADRAO = "deepseek/deepseek-chat"


def _get_api_key() -> Optional[str]:
    """Obtém a chave da API do Hermes Operator."""
    # 1. Variável de ambiente
    key = os.getenv("HERMES_OPERATOR_API_KEY")
    if key:
        return key

    # 2. .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("HERMES_OPERATOR_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # 3. Streamlit Secrets
    try:
        import streamlit as st
        return st.secrets.get("HERMES_OPERATOR_API_KEY")
    except Exception:
        pass

    return None


def _get_api_url() -> str:
    """Obtém a URL da API, com fallback para o padrão."""
    url = os.getenv("HERMES_OPERATOR_API_URL")
    if url:
        return url
    try:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("HERMES_OPERATOR_API_URL")
        if url:
            return url
    except Exception:
        pass
    return API_URL_PADRAO


def _get_modelo() -> str:
    """Obtém o modelo configurado, com fallback para o padrão."""
    modelo = os.getenv("HERMES_OPERATOR_MODEL")
    if modelo:
        return modelo
    try:
        from dotenv import load_dotenv
        load_dotenv()
        modelo = os.getenv("HERMES_OPERATOR_MODEL")
        if modelo:
            return modelo
    except Exception:
        pass
    return MODELO_PADRAO


class HermesOperatorClient:
    """
    Cliente para o Hermes Operator (API OpenAI-compatível).

    Conecta ao endpoint do Hugging Face Space que faz proxy via OpenRouter
    para o modelo deepseek/deepseek-chat.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        modelo: Optional[str] = None,
    ):
        self._api_key = api_key or _get_api_key()
        self.api_url = api_url or _get_api_url()
        self.modelo = modelo or _get_modelo()
        # Métricas
        self._total_requests = 0
        self._total_response_time = 0.0
        self._last_response_time = 0.0
        self._total_tokens_estimate = 0
        self._cache_hits = 0
        self._cache_misses = 0

    @property
    def disponivel(self) -> bool:
        """Verifica se a chave está configurada."""
        return bool(self._api_key)

    def gerar_texto(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 8192,
    ) -> str:
        """
        Gera texto usando o Hermes Operator via API OpenAI-compatível.

        Args:
            prompt: Mensagem do usuário.
            system_prompt: Instrução de sistema (persona).
            temperatura: Criatividade (0.0 a 1.0).
            max_tokens: Máximo de tokens na resposta.

        Returns:
            Texto gerado.
        """
        import httpx
        import time

        system_content = system_prompt or PERSONA_RAG

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperatura,
            "max_tokens": max_tokens,
        }

        try:
            inicio = time.time()
            with httpx.Client(timeout=120) as client:
                resposta = client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                )
                resposta.raise_for_status()
                data = resposta.json()
                conteudo = data["choices"][0]["message"]["content"] or ""
            self._last_response_time = time.time() - inicio
            self._total_response_time += self._last_response_time
            self._total_requests += 1
            self._total_tokens_estimate += len(conteudo) // 4
            self._cache_misses += 1
            return conteudo
        except httpx.HTTPStatusError as e:
            logger.error(f"Hermes Operator HTTP {e.response.status_code}: {e.response.text[:200]}")
            raise RuntimeError(
                f"Erro HTTP {e.response.status_code} do Hermes Operator. "
                f"Detalhes: {e.response.text[:200]}"
            )
        except httpx.TimeoutException:
            logger.error("Hermes Operator: timeout após 120s")
            raise RuntimeError(
                "Hermes Operator não respondeu dentro do tempo limite (120s). "
                "O servidor pode estar ocupado ou indisponível."
            )
        except Exception as e:
            logger.error(f"Hermes Operator: erro inesperado: {e}")
            raise RuntimeError(f"Erro ao comunicar com Hermes Operator: {e}")

    def obter_metricas(self) -> dict:
        """Retorna métricas de performance do cliente."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0.0
        tempo_medio = (
            self._total_response_time / self._total_requests
            if self._total_requests > 0
            else 0.0
        )
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(hit_rate, 1),
            "total_requests": self._total_requests,
            "ultimo_tempo_resposta": round(self._last_response_time, 2),
            "tempo_medio_resposta": round(tempo_medio, 2),
            "tokens_estimados": self._total_tokens_estimate,
        }


# Singleton
_cliente_global: Optional[HermesOperatorClient] = None


def get_cliente_hermes() -> HermesOperatorClient:
    """Obtém instância singleton do HermesOperatorClient."""
    global _cliente_global
    if _cliente_global is None:
        _cliente_global = HermesOperatorClient()
    return _cliente_global
