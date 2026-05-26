"""
Módulo para geração de legendas para Instagram usando Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.constants import TOM_ESTILO
from utils.helpers import sanitizar_html, tratar_erro_gemini

logger = logging.getLogger(__name__)

TOP_K = 6


def _buscar_contexto(top_k: int = TOP_K) -> str:
    """Busca contexto relevante do vector store."""
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return ""

        consulta = "Ensina Mais Turma da Monica Tatuapé marketing franquia educação"
        resultados = collection.query(
            query_texts=[consulta],
            n_results=min(top_k, count),
            include=["documents"],
        )
        docs = resultados.get("documents", [[]])
        return "\n\n".join(docs) if docs else ""

    except Exception as e:
        logger.warning(f"Erro ao buscar contexto: {e}")
        return ""


def gerar_legenda(
    image,
    tom: str = "Educativo",
    tema: str = "",
    instrucoes: str = "",
    top_k: int = TOP_K,
) -> dict:
    """
    Gera 3 opções de legenda para Instagram com base em uma imagem.

    Returns:
        Dicionário com status, conteúdo, contexto_usado e tom.
    """
    if tom not in TOM_ESTILO:
        logger.warning(f"Tom '{tom}' não reconhecido, usando 'Educativo'")
        tom = "Educativo"

    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        if not cliente.api_key_configured:
            return {
                "status": "erro",
                "mensagem": "GEMINI_API_KEY não configurada.",
                "legendas": [],
                "hashtags": [],
            }
    except GeminiAPIKeyError:
        return {
            "status": "erro",
            "mensagem": "GEMINI_API_KEY não configurada.",
            "legendas": [],
            "hashtags": [],
        }

    contexto = _buscar_contexto(top_k)
    estilo = TOM_ESTILO.get(tom, TOM_ESTILO["Educativo"])
    prompt = _construir_prompt(tom, estilo, tema, instrucoes, contexto)

    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        conteudo = cliente.gerar_com_imagem(
            prompt=prompt,
            imagem=image,
            usar_cache=False,
            temperatura=0.7,
            max_tokens=4096,
        )

        if not conteudo:
            return {
                "status": "erro",
                "mensagem": "Gemini retornou resposta vazia.",
                "legendas": [],
                "hashtags": [],
            }

        conteudo = sanitizar_html(conteudo)

        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
            "tom": tom,
        }

    except GeminiError as e:
        return {
            "status": "erro",
            "mensagem": tratar_erro_gemini(e),
            "legendas": [],
            "hashtags": [],
        }


def _construir_prompt(
    tom: str,
    estilo: str,
    tema: str,
    instrucoes: str,
    contexto: str,
) -> str:
    """Constrói o prompt completo para geração de legendas."""
    prompt = (
        "Você é um social media especializado em franquias educacionais, "
        "criando conteúdo para o Instagram da unidade Tatuapé da rede "
        "Ensina Mais Turma da Mônica.\n\n"
        f"TOM: {tom}\n{estilo}\n\n"
        "Analise a imagem fornecida e gere **3 opções de legenda** para o Instagram.\n\n"
        "Cada opção deve conter:\n"
        "- Um texto de legenda envolvente (2-4 parágrafos curtos)\n"
        "- Entre 5-10 hashtags relevantes\n"
    )

    if tema:
        prompt += f"\nTEMA SUGERIDO: {tema}\n"

    if instrucoes:
        prompt += f"\nINSTRUÇÕES ADICIONAIS: {instrucoes}\n"

    if contexto:
        prompt += (
            f"\nUse as informações abaixo sobre a unidade para personalizar:\n"
            f"{contexto}\n\n"
        )

    prompt += (
        "\nRegras:\n"
        "1. Relacione a legenda com o que aparece na imagem.\n"
        "2. Use linguagem adequada para pais de alunos (público-alvo).\n"
        "3. Inclua calls-to-action relevantes (comente, compartilhe, marque).\n"
        "4. Se o contexto mencionar serviços específicos, destaque-os.\n"
        "5. Varie o formato entre as 3 opções (uma mais curta, uma mais detalhada, etc).\n\n"
        "Formato da resposta:\n"
        "---\n"
        "## Opção 1: [título informal]\n"
        "[texto da legenda]\n\n"
        "**Hashtags:** #tag1 #tag2 ...\n"
        "---\n"
        "## Opção 2: [título informal]\n"
        "[texto da legenda]\n\n"
        "**Hashtags:** #tag1 #tag2 ...\n"
        "---\n"
        "## Opção 3: [título informal]\n"
        "[texto da legenda]\n\n"
        "**Hashtags:** #tag1 #tag2 ...\n"
        "---\n"
    )

    return prompt
