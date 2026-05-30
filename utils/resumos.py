"""
Módulo para geração de resumos de documentos usando Hermes Operator.

Chamado após upload de PDF/URL/HTML para gerar uma descrição curta
do documento — usada na listagem e busca.
"""

import logging

from utils.hermes_operator_client import get_cliente_hermes
from utils.prompts import PERSONA_RESUMOS

logger = logging.getLogger(__name__)

TAMANHO_MAXIMO_TEXTO = 8_000
TAMANHO_MAXIMO_RESUMO = 200


def gerar_resumo(texto: str, fonte: str = "documento") -> str:
    """
    Gera um resumo ultraconciso (1 frase, até 25 palavras) do texto fornecido.

    Args:
        texto: Conteúdo do documento a ser resumido.
        fonte: Origem do documento (pdf, url, texto, etc.).

    Returns:
        Frase resumo ou mensagem de erro.
    """
    texto_cortado = texto[:TAMANHO_MAXIMO_TEXTO]
    if not texto_cortado.strip():
        return "Erro: texto vazio"

    prompt = (
        "Leia o texto abaixo e produza UMA frase curta (máximo 25 palavras) "
        "que descreva exatamente do que o documento trata. "
        "Seja direta: capture o assunto central, não liste detalhes.\n\n"
        f"Fonte do documento: {fonte}\n\n"
        f"TEXTO:\n{texto_cortado}\n\n"
        "RESUMO (uma frase, máx. 25 palavras):"
    )

    try:
        hermes = get_cliente_hermes()
        if not hermes.disponivel:
            return "Erro: chave do Hermes Operator não configurada"

        resumo = hermes.gerar_texto(
            prompt=prompt,
            system_prompt=PERSONA_RESUMOS,
            temperatura=0.3,
            max_tokens=100,
        )
        return resumo[:TAMANHO_MAXIMO_RESUMO].strip()

    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return f"Erro ao gerar resumo: {str(e)}"
