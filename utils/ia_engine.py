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
TOP_K = 12


def buscar_contexto(pergunta: str, top_k: int = TOP_K) -> tuple[str, list[dict]]:
    """Busca chunks relevantes, com expansão de consulta para melhor recall."""
    collection = _get_collection()
    
    # Expansão de consulta: busca com múltiplas variações da pergunta
    variacoes = [pergunta]
    
    # Extrair palavras-chave e criar variações
    palavras = pergunta.lower().split()
    nome_rede = [p for p in palavras if 'ensina' in p or 'mais' in p or 'mônica' in p or 'turma' in p]
    
    if "diferencial" in palavras or "competitivo" in palavras or "vantagem" in palavras:
        # Pergunta sobre diferenciais - buscar também por benefícios/programas
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
        
        for doc, md, dist in zip(documentos[0], (metadatas[0] if metadatas and metadatas[0] else []), (distances[0] if distances and distances[0] else [])):
            # Dedicar snippet como chave
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

    except GeminiAPIKeyError as e:
        return {"resposta": f"Erro: {e}", "fontes": []}
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
