"""
Módulo principal do motor RAG — consulta a base vetorial e gera respostas.

Usa Hermes Operator (deepseek/deepseek-chat via OpenRouter) como provedor
principal, com fallback para Gemini e depois Groq.
"""

import logging
import time

from utils.config import MODELO_GEMINI, TOP_K_PADRAO
from utils.documentos import _get_collection
from utils.hermes_operator_client import (
    HermesOperatorClient,
    get_cliente_hermes,
)
from utils.gemini_client import (
    GeminiError,
    GeminiAPIKeyError,
    GeminiQuotaError,
    GeminiDailyQuotaError,
    GeminiServerError,
    GeminiSafetyError,
    get_cliente,
)
from utils.groq_client import get_cliente_groq
from utils.prompts import PERSONA_RAG, formatar_contexto

logger = logging.getLogger(__name__)

MODELO = MODELO_GEMINI
TOP_K = TOP_K_PADRAO


def buscar_contexto(pergunta: str, top_k: int = TOP_K) -> tuple[str, list[dict]]:
    """Busca chunks relevantes, com expansão de consulta para melhor recall."""
    collection = _get_collection()

    # Expansão de consulta: busca com múltiplas variações da pergunta
    variacoes = [pergunta]

    # Extrair palavras-chave e criar variações
    palavras = pergunta.lower().split()
    nome_rede = [p for p in palavras if 'ensina' in p or 'mais' in p or 'mônica' in p or 'turma' in p]

    if "diferencial" in palavras or "competitivo" in palavras or "vantagem" in palavras:
        if nome_rede:
            variacoes.append(f"programas educacionais {' '.join(nome_rede)}")
            variacoes.append(f"benefícios ensino {' '.join(nome_rede)}")

    if "metodologia" in palavras or "ensino" in palavras:
        if nome_rede:
            variacoes.append(f"{' '.join(nome_rede)} robótica tecnologia apoio escolar")

    # Executar busca com todas as variações
    todos_textos = []
    todos_fontes = []
    vistos = set()

    for v in variacoes:
        try:
            resultados = collection.query(
                query_texts=[v], n_results=top_k // len(variacoes) + 1,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            continue

        documentos = resultados.get("documents", [[]])
        metadatas = resultados.get("metadatas", [[]])
        distances = resultados.get("distances", [[]])

        if not documentos or not documentos[0]:
            continue

        for doc, md, dist in zip(documentos[0],
                                  (metadatas[0] if metadatas and metadatas[0] else []),
                                  (distances[0] if distances and distances[0] else [])):
            chave = doc[:100]
            if chave in vistos:
                continue
            vistos.add(chave)
            todos_textos.append(doc)
            fonte = {"fonte": md.get("fonte", "desconhecida"), "relevancia": round(1 - dist, 3)}
            for k in ("arquivo", "url", "perfil", "titulo"):
                if md.get(k):
                    fonte[k] = md[k]
            todos_fontes.append(fonte)

    # Limitar ao top_k mais relevantes
    combinados = list(zip(todos_textos, todos_fontes))
    combinados.sort(key=lambda x: -x[1]["relevancia"])
    combinados = combinados[:top_k]

    if not combinados:
        return "", []

    textos = [t for t, _ in combinados]
    fontes = [f for _, f in combinados]

    return "\n\n".join(textos), fontes


def perguntar(pergunta: str, contexto: str = None) -> dict:
    """
    Faz uma pergunta RAG: busca contexto na base vetorial e gera resposta.

    Ordem de tentativa:
    1. Hermes Operator (deepseek via OpenRouter) — PRIMÁRIO
    2. Gemini (fallback se Hermes Operator falhar)
    3. Groq (fallback final)

    Args:
        pergunta: Pergunta do usuário.
        contexto: Contexto opcional já fornecido (para reuso).

    Returns:
        Dicionário com resposta, fontes e provedor usado.
    """
    fontes = []
    if not contexto:
        contexto, fontes = buscar_contexto(pergunta)

    if not contexto:
        return {
            "resposta": (
                "Nenhum documento foi carregado ainda. "
                "Faça upload de PDFs primeiro."
            ),
            "fontes": [],
        }

    prompt = _construir_prompt_rag(pergunta, contexto)

    # ── 1. Tentar Hermes Operator (primário) ──
    try:
        hermes = get_cliente_hermes()
        if not hermes.disponivel:
            logger.warning("Hermes Operator não configurado, pulando para Gemini...")
        else:
            resposta = hermes.gerar_texto(
                prompt=prompt,
                system_prompt=PERSONA_RAG,
                temperatura=0.4,
                max_tokens=8192,
            )
            return {"resposta": resposta, "fontes": fontes, "provedor": "hermes_operator"}
    except RuntimeError as e:
        logger.warning(f"Hermes Operator falhou: {e}. Tentando Gemini...")
    except Exception as e:
        logger.warning(f"Hermes Operator erro inesperado: {e}. Tentando Gemini...")

    # ── 2. Tentar Gemini (fallback) ──
    try:
        cliente = get_cliente(modelo=MODELO)
        resposta = cliente.gerar_texto(
            prompt=prompt,
            system_instruction=PERSONA_RAG,
            usar_cache=True,
            temperatura=0.4,
            max_tokens=8192,
        )
        return {"resposta": resposta, "fontes": fontes, "provedor": "gemini"}
    except GeminiDailyQuotaError:
        logger.warning("Gemini em cota diária, tentando Groq...")
    except GeminiQuotaError:
        logger.warning("Gemini em rate limit, tentando Groq...")
        time.sleep(3)
    except GeminiServerError:
        logger.warning("Gemini indisponível, tentando Groq...")
    except GeminiAPIKeyError as e:
        return {"resposta": f"Erro: {e}", "fontes": [], "provedor": ""}
    except GeminiSafetyError:
        return {
            "resposta": "O conteúdo foi bloqueado pelos filtros de segurança do Gemini.",
            "fontes": [], "provedor": "",
        }
    except GeminiError as e:
        logger.error(f"Erro Gemini: {e}")
        return {
            "resposta": f"Erro ao comunicar com o Gemini: {e.message[:200]}",
            "fontes": [], "provedor": "",
        }

    # ── 3. Groq (fallback final) ──
    try:
        groq = get_cliente_groq()
        if not groq.disponivel:
            return {
                "resposta": (
                    "⚠️ Hermes Operator e Gemini falharam, e o Groq (fallback) "
                    "não está configurado. Verifique as chaves de API ou tente novamente."
                ),
                "fontes": [], "provedor": "",
            }

        resposta = groq.gerar_texto(
            prompt=prompt,
            system_prompt=PERSONA_RAG,
            temperatura=0.4,
            max_tokens=8192,
        )
        return {
            "resposta": resposta + "\n\n🤖 *Respondido via Groq (fallback)*",
            "fontes": fontes,
            "provedor": "groq",
        }
    except Exception as e:
        logger.error(f"Groq fallback falhou: {e}")
        return {
            "resposta": (
                "Todos os provedores falharam. "
                f"Hermes Operator: indisponível. "
                f"Gemini: cota esgotada. "
                f"Groq: {str(e)[:100]}."
            ),
            "fontes": [], "provedor": "",
        }


def _construir_prompt_rag(pergunta: str, contexto: str) -> str:
    """Constrói o prompt de usuário para a consulta RAG."""
    ctx = formatar_contexto(contexto)
    if not ctx:
        return f"Pergunta: {pergunta}"

    return (
        f"{ctx}\n"
        f"Com base SOMENTE no contexto acima, responda:\n\n"
        f"Pergunta: {pergunta}\n\n"
        f"IMPORTANTE:\n"
        f"1. Se não encontrar a resposta no contexto, diga claramente que não há "
        f"informação suficiente — NÃO invente.\n"
        f"2. Quando possível, indique de qual documento a informação veio.\n"
        f"3. Se houver dados numéricos, destaque-os.\n"
        f"4. Estruture a resposta em tópicos quando ajudar na clareza."
    )
