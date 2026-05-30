"""
Módulo para geração de legendas para Instagram — Gemini como padrão.

O Gemini analisa a imagem enviada para gerar legendas contextuais.
Caso o Gemini esteja indisponível, cai para Hermes Operator (apenas texto).
"""

import logging

from utils.documentos import _get_collection
from utils.hermes_operator_client import get_cliente_hermes
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.constants import TOM_ESTILO
from utils.helpers import sanitizar_html, tratar_erro_ia
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
    Gera 3 opções de legenda para Instagram.

    Usa **Gemini** como padrão (analisa a imagem + contexto).
    Se Gemini falhar, usa Hermes Operator como fallback (apenas texto).

    Args:
        image: Objeto de imagem (PIL ou bytes) para análise via Gemini.
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

    contexto = _buscar_contexto(top_k)
    estilo = TOM_ESTILO.get(tom, TOM_ESTILO["Educativo"])
    prompt = _construir_prompt(tom, estilo, tema, instrucoes, contexto)

    # ── 1. Gemini (padrão) — com análise de imagem ──
    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        if cliente.api_key_configured:
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
    except (GeminiError, GeminiAPIKeyError) as e:
        logger.warning(f"Gemini falhou, tentando Hermes Operator: {e}")
    except Exception as e:
        logger.error(f"Gemini erro inesperado, tentando Hermes Operator: {e}")

    # ── 2. Fallback: Hermes Operator (apenas texto) ──
    hermes = get_cliente_hermes()
    if hermes.disponivel:
        try:
            conteudo = hermes.gerar_texto(
                prompt=prompt,
                system_prompt=PERSONA_SOCIAL_MEDIA,
                temperatura=0.7,
                max_tokens=4096,
            )
            if conteudo:
                conteudo = sanitizar_html(conteudo)
                return {
                    "status": "ok",
                    "conteudo": conteudo,
                    "contexto_usado": bool(contexto),
                    "tom": tom,
                }
        except Exception as e:
            logger.error(f"Hermes Operator fallback também falhou: {e}")

    # ── 3. Nenhum funcionou ──
    return {
        "status": "erro",
        "mensagem": (
            "Nenhum provedor de IA disponível para gerar legendas. "
            "Verifique as chaves de API."
        ),
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
        "Gere 3 opções de legenda para o Instagram da franquia Ensina Mais Turma da Mônica.",
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
        "1. Use linguagem adequada para pais de alunos (público-alvo).",
        "2. Inclua calls-to-action relevantes (comente, compartilhe, marque).",
        "3. Se o contexto mencionar serviços específicos, destaque-os.",
        "4. Varie o formato entre as 3 opções (uma mais curta, uma mais detalhada, etc).",
        "5. NÃO use tags HTML. Use apenas Markdown.",
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
