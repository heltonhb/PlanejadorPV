"""
Cliente para API Groq — fallback quando Gemini atinge cota diária.

Groq oferece inferência rápida com modelos como Llama 3, Mixtral, etc.
Free tier: 30 RPM, sem limite diário conhecido.
"""

import logging
import os
from typing import Optional

from utils.prompts import PERSONA_RAG

logger = logging.getLogger(__name__)

MODELOS_DISPONIVEIS = [
    "llama-3.3-70b-versatile",  # mais capaz (70B)
    "llama-3.1-8b-instant",     # mais rápido (8B)
]

MODELO_PADRAO = "llama-3.1-8b-instant"


def _get_groq_key() -> Optional[str]:
    """Obtém chave da API Groq."""
    # 1. Variável de ambiente
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key

    # 2. .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # 3. Streamlit Secrets
    try:
        import streamlit as st
        return st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    return None


class GroqClient:
    """Cliente para API Groq com fallbacks e cache."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        modelo: str = MODELO_PADRAO,
    ):
        self._api_key = api_key or _get_groq_key()
        self.modelo = modelo
        self._client = None

    @property
    def disponivel(self) -> bool:
        """Verifica se a chave está configurada."""
        return bool(self._api_key)

    def _get_client(self):
        """Obtém ou cria o cliente Groq."""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self._api_key)
        return self._client

    def gerar_texto(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 8192,
    ) -> str:
        """Gera texto usando Groq.

        Args:
            prompt: Mensagem do usuário.
            system_prompt: Instrução de sistema (persona). Usa PERSONA_RAG como padrão.
            temperatura: Criatividade (0.0 a 1.0).
            max_tokens: Máximo de tokens na resposta.

        Returns:
            Texto gerado.
        """
        if not self._api_key:
            raise RuntimeError("GROQ_API_KEY não configurada.")

        system_content = system_prompt or PERSONA_RAG

        client = self._get_client()

        resposta = client.chat.completions.create(
            model=self.modelo,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
            ],
            temperature=temperatura,
            max_tokens=max_tokens,
        )

        return resposta.choices[0].message.content or ""


# Singleton
_cliente_global: Optional[GroqClient] = None


def get_cliente_groq() -> GroqClient:
    """Obtém instância singleton do cliente Groq."""
    global _cliente_global
    if _cliente_global is None:
        _cliente_global = GroqClient()
    return _cliente_global
