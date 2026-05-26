"""
Módulo para geração de legendas para Instagram usando Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.constants import TOM_ESTILO
from utils.helpers import sanitizar_html, tratar_erro_gemini
from utils.prompts import PERSONA_SOCIAL_MEDIA, formatar_contexto

logger = logging.getLogger(__name__)

TOP_K = 6


def _buscar_contexto(top_k: int = TOP_K) -> str:
    """Busca contexto relevante da base vetorial."""
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
        return "\n\n".join(docs[0]) if docs and docs[0] else ""

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

    Args:
        image: Objeto de imagem (PIL ou bytes) para análise.
        tom: Tom da legenda (ver TOM_ESTILO em constants.py).
        tema: Tema sugerido opcional.
        instrucoes: Instruções adicionais opcionais.
        top_k: Número de chunks de contexto a buscar.

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
        conteudo = cliente.gerar_com_imagem(
            prompt=prompt,
            imagem=image,
            system_instruction=PERSONA_SOCIAL_MEDIA,
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
    """Constrói o prompt de usuário para geração de legendas."""
    linhas = [
        "Analise a imagem fornecida e gere 3 opções de legenda para o Instagram.",
        "",
        "=== CONFIGURAÇÃO ===",
        f"TOM: {tom}",
        estilo,
    ]

    if tema:
        linhas.append(f"TEMA SUGERIDO: {tema}")

    if instrucoes:
        linhas.append(f"INSTRUÇÕES ADICIONAIS: {instrucoes}")

    ctx = formatar_contexto(contexto)
    if ctx:
        linhas.append(ctx)

    linhas += [
        "",
        "REGRAS:",
        "1. Relacione a legenda com o que aparece na imagem.",
        "2. Use linguagem adequada para pais de alunos (público-alvo).",
        "3. Inclua calls-to-action relevantes (comente, compartilhe, marque).",
        "4. Se o contexto mencionar serviços específicos, destaque-os.",
        "5. Varie o formato entre as 3 opções (uma mais curta, uma mais detalhada, etc).",
        "6. NÃO use tags HTML. Use apenas Markdown.",
        "",
        "FORMATO DA RESPOSTA:",
        "---",
        "## Opção 1: [título informal]",
        "[texto da legenda]",
        "",
        "**Hashtags:** #tag1 #tag2 ...",
        "---",
        "## Opção 2: [título informal]",
        "[texto da legenda]",
        "",
        "**Hashtags:** #tag1 #tag2 ...",
        "---",
        "## Opção 3: [título informal]",
        "[texto da legenda]",
        "",
        "**Hashtags:** #tag1 #tag2 ...",
        "---",
    ]

    return "\n".join(linhas)
