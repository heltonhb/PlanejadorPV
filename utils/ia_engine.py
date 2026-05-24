"""
Módulo principal do motor RAG — consulta a base vetorial e gera respostas com Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import (
    GeminiError,
    GeminiAPIKeyError,
    GeminiQuotaError,
    GeminiDailyQuotaError,
    GeminiServerError,
    GeminiSafetyError,
    get_cliente,
)

logger = logging.getLogger(__name__)

MODELO = "gemini-2.5-flash"
TOP_K = 5


def buscar_contexto(pergunta: str, top_k: int = TOP_K) -> tuple[str, list[dict]]:
    collection = _get_collection()
    resultados = collection.query(
        query_texts=[pergunta], n_results=top_k, include=["documents", "metadatas", "distances"],
    )
    documentos = resultados.get("documents", [[]])
    metadatas = resultados.get("metadatas", [[]])
    distances = resultados.get("distances", [[]])

    if not documentos or not documentos[0]:
        return "", []

    textos = documentos[0]
    metas = metadatas[0] if metadatas and metadatas[0] else []
    dists = distances[0] if distances and distances[0] else []

    fontes = []
    for md, dist in zip(metas, dists):
        fonte = {"fonte": md.get("fonte", "desconhecida"), "relevancia": round(1 - dist, 3)}
        if md.get("arquivo"):
            fonte["arquivo"] = md["arquivo"]
        if md.get("url"):
            fonte["url"] = md["url"]
        if md.get("perfil"):
            fonte["perfil"] = md["perfil"]
        if md.get("titulo"):
            fonte["titulo"] = md["titulo"]
        fontes.append(fonte)

    return "\n\n".join(documentos[0]), fontes


def perguntar(pergunta: str, contexto: str = None) -> dict:
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

    prompt = (
        f"Você é um consultor de marketing especializado em "
        f"franquias educacionais, com foco na rede Ensina Mais Turma da Mônica. "
        f"Responda à pergunta usando APENAS as informações fornecidas nos "
        f"documentos de referência abaixo.\n\n"
        f"Regras:\n"
        f"1. Seja direto e prático — o usuário é um franqueado que quer ações aplicáveis.\n"
        f"2. Sempre que possível, estruture a resposta com tópicos ou seções claras.\n"
        f"3. Se mencionar dados numéricos, destaque-os.\n"
        f"4. Se não encontrar a resposta nos documentos, diga claramente que "
        f"não há informação suficiente.\n"
        f"5. Mantenha o tom profissional, mas acessível — o usuário não é "
        f"especialista em marketing.\n\n"
        f"Documentos de referência:\n{contexto}\n\n"
        f"Pergunta: {pergunta}"
    )

    try:
        cliente = get_cliente(modelo=MODELO)
        resposta = cliente.gerar_texto(
            prompt=prompt,
            usar_cache=True,
            temperatura=0.7,
            max_tokens=2048,
        )
        return {"resposta": resposta, "fontes": fontes}

    except GeminiAPIKeyError:
        return {"resposta": "Erro: GEMINI_API_KEY não configurada.", "fontes": []}
    except GeminiDailyQuotaError:
        return {
            "resposta": "⚠️ Limite **diário** de requisições excedido. O Google Gemini resetará a cota automaticamente — você poderá usar o app novamente amanhã.",
            "fontes": [],
        }
    except GeminiQuotaError:
        return {
            "resposta": "Limite de requisições excedido. Aguarde alguns minutos e tente novamente.",
            "fontes": [],
        }
    except GeminiServerError:
        return {
            "resposta": "Servidor do Gemini temporariamente indisponível. Tente novamente em alguns instantes.",
            "fontes": [],
        }
    except GeminiSafetyError:
        return {
            "resposta": "O conteúdo foi bloqueado pelos filtros de segurança do Gemini.",
            "fontes": [],
        }
    except GeminiError as e:
        logger.error(f"Erro Gemini: {e}")
        return {
            "resposta": f"Erro ao comunicar com o Gemini: {e.message[:200]}",
            "fontes": [],
        }
