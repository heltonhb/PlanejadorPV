"""
Módulo para geração de resumos de documentos usando Gemini.
"""

import logging

from utils.config import MODELO_GEMINI
from utils.gemini_client import (
    GeminiError,
    GeminiAPIKeyError,
    get_cliente,
)

logger = logging.getLogger(__name__)

MODELO = MODELO_GEMINI
TAMANHO_MAXIMO_TEXTO = 8000
TAMANHO_MAXIMO_RESUMO = 250


def gerar_resumo(texto: str, fonte: str = "documento") -> str:
    """
    Gera um resumo humanizado de 1-2 frases sobre o conteúdo do texto.
    
    Args:
        texto: Texto original a ser resumido.
        fonte: Nome/fonte do documento para contexto.
        
    Returns:
        Resumo gerado ou mensagem de erro.
    """
    if not texto or not texto.strip():
        logger.debug("Texto vazio fornecido para resumo")
        return "Erro: texto vazio"
    
    texto_cortado = texto[:TAMANHO_MAXIMO_TEXTO]
    if not texto_cortado.strip():
        return "Erro: texto vazio"
    
    prompt = (
        f"Leia o texto abaixo e escreva UMA frase curta (máximo 25 palavras) "
        f"descrevendo do que o documento trata. "
        f"Use linguagem natural e direta. "
        f"Fonte: {fonte}.\n\n"
        f"Texto:\n{texto_cortado}\n\n"
        "Resumo:"
    )
    
    try:
        cliente = get_cliente(modelo=MODELO)
        resumo = cliente.gerar_texto(
            prompt=prompt,
            usar_cache=True,
            temperatura=0.3,
            max_tokens=100,
        )
        return resumo[:TAMANHO_MAXIMO_RESUMO].strip()
    
    except GeminiAPIKeyError:
        logger.warning("GEMINI_API_KEY não configurada")
        return "Erro: GEMINI_API_KEY não configurada"
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return f"Erro ao gerar resumo: {str(e)}"


def gerar_resumo_batch(textos: list[str], fontes: list[str] = None) -> list[str]:
    """Gera resumos para múltiplos textos em lote."""
    if fontes is None:
        fontes = ["documento"] * len(textos)
    
    return [
        gerar_resumo(texto, fonte)
        for texto, fonte in zip(textos, fontes)
    ]
