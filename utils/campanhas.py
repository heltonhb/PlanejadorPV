import os

from dotenv import load_dotenv
from google import genai

from utils.documentos import _get_collection

load_dotenv()

MODELO = "gemini-2.5-flash"

OBJETIVOS = [
    "Atrair novos alunos",
    "Reaquecer leads antigos",
    "Fidelizar alunos atuais",
    "Divulgar novo serviço ou curso",
    "Promover matrículas (ação sazonal)",
    "Gerar indicação de alunos",
]

PUBLICOS = [
    "Fundamental I (6 a 10 anos)",
    "Fundamental II (11 a 15 anos)",
    "Ambos (Fundamental I e II)",
    "Responsáveis dos alunos",
]

SERVICOS = [
    "Apoio escolar — Português",
    "Apoio escolar — Matemática",
    "Tecnologia — Programação",
    "Tecnologia — Robótica",
    "Todos os serviços",
]


def _buscar_contexto_campanha(top_k: int = 8) -> str:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return ""
    consulta = "marketing campanhas franquia educacional Ensina Mais Tatuapé"
    resultados = collection.query(
        query_texts=[consulta], n_results=min(top_k, count),
        include=["documents"],
    )
    docs = resultados.get("documents", [[]])
    if docs and docs[0]:
        return "\n\n".join(docs[0])
    return ""


def _get_gemini_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def gerar_campanha(objetivo: str, publico: str, servico: str) -> dict:
    api_key = _get_gemini_key()
    if not api_key:
        return {"status": "erro", "mensagem": "GEMINI_API_KEY não configurada.", "conteudo": ""}

    contexto = _buscar_contexto_campanha()

    prompt = (
        f"Crie uma campanha de marketing completa para:\n\n"
        f"Franquia: Ensina Mais Turma da Mônica\n"
        f"Unidade: Tatuapé - SP\n"
        f"Objetivo: {objetivo}\n"
        f"Público-alvo: {publico}\n"
        f"Serviço: {servico}\n"
    )
    if contexto:
        prompt += (
            f"\nUse as informações dos documentos abaixo para personalizar:\n"
            f"{contexto}\n\n"
        )
    prompt += (
        f"\nFormato da resposta (use Markdown):\n\n"
        f"## Nome da Campanha\n"
        f"[nome criativo]\n\n"
        f"### Descrição\n"
        f"[descrição da campanha]\n\n"
        f"### Canais\n"
        f"- **Instagram**: [ideias de posts, stories ou reels]\n"
        f"- **WhatsApp**: [texto ou roteiro para disparo]\n"
        f"- **Material Impresso**: [ideia de flyer, cartaz ou panfleto]\n\n"
        f"### Cronograma\n"
        f"- **Semana 1**: [ação]\n"
        f"- **Semana 2**: [ação]\n"
        f"- **Semana 3**: [ação]\n\n"
        f"### Investimento Sugerido\n"
        f"[estimativa com base em ações similares]\n\n"
        f"### Métricas de Sucesso\n"
        f"[como medir se a campanha deu certo]\n\n"
        f"Regras:\n"
        f"1. Seja específico e acionável — o usuário é um franqueado.\n"
        f"2. Adapte a linguagem e os exemplos ao público-alvo informado.\n"
        f"3. Se houver dados dos documentos, use-os.\n"
        f"4. Mantenha tom profissional mas acessível."
    )

    client = genai.Client(api_key=api_key)
    try:
        resposta = client.models.generate_content(model=MODELO, contents=prompt)
    except Exception as e:
        erro = str(e)
        if "API_KEY" in erro.upper() or "not found" in erro.lower():
            msg = "Chave da API Gemini inválida ou não encontrada."
        elif "quota" in erro.lower() or "rate" in erro.lower() or "429" in erro:
            msg = "Limite de requisições excedido. Aguarde alguns minutos e tente novamente."
        elif "500" in erro or "503" in erro or "server" in erro.lower():
            msg = "Servidor do Gemini temporariamente indisponível. Tente novamente em alguns instantes."
        elif "safety" in erro.lower() or "blocked" in erro.lower():
            msg = "O conteúdo foi bloqueado pelos filtros de segurança do Gemini. Tente reformular a solicitação."
        else:
            msg = f"Erro ao comunicar com o Gemini: {erro[:200]}"
        return {"status": "erro", "mensagem": msg, "conteudo": ""}

    return {
        "status": "ok",
        "conteudo": resposta.text,
        "contexto_usado": bool(contexto),
    }
