import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODELO = "gemini-2.5-flash"


def _get_gemini_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def gerar_resumo(texto: str, fonte: str = "documento") -> str:
    """Gera um resumo humanizado de 1-2 frases sobre o conteúdo do texto."""
    api_key = _get_gemini_key()
    if not api_key:
        return ""

    texto_cortado = texto[:8000]
    if not texto_cortado.strip():
        return ""

    prompt = (
        f"Leia o texto abaixo e escreva UMA frase curta (máximo 25 palavras) "
        f"descrevendo do que o documento trata. "
        f"Use linguagem natural e direta. "
        f"Fonte: {fonte}.\n\n"
        f"Texto:\n{texto_cortado}\n\n"
        "Resumo:"
    )

    client = genai.Client(api_key=api_key)
    try:
        resposta = client.models.generate_content(
            model=MODELO,
            contents=[prompt],
        )
        resumo = (resposta.text or "").strip()
        return resumo[:250]
    except Exception:
        return ""
