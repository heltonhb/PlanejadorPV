import os
from typing import Optional


def get_gemini_key() -> Optional[str]:
    """
    Obtém a chave da API Gemini das variáveis de ambiente
    ou dos secrets do Streamlit.
    """
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def formatar_numero(numero: int | float) -> str:
    """Formata números com separadores de milhar."""
    return f"{numero:,}".replace(",", ".")


def truncar_texto(texto: str, max_length: int = 100, sufixo: str = "...") -> str:
    """Trunca texto longo adicionando sufixo."""
    if len(texto) <= max_length:
        return texto
    return texto[:max_length - len(sufixo)] + sufixo
