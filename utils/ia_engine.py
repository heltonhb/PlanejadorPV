import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from utils.documentos import CHROMA_PATH, COLLECTION_NAME

load_dotenv()

MODELO = "gemini-2.5-flash"
TOP_K = 5


def _get_collection():
    CHROMA_PATH.mkdir(exist_ok=True)
    client = PersistentClient(str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
    )


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


def _get_gemini_key() -> Optional[str]:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


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

    api_key = _get_gemini_key()
    if not api_key:
        return {"resposta": "Erro: GEMINI_API_KEY não configurada.", "fontes": []}

    client = genai.Client(api_key=api_key)
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
    resposta = client.models.generate_content(
        model=MODELO,
        contents=prompt,
    )
    return {"resposta": resposta.text, "fontes": fontes}
