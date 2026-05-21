import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from utils.documentos import _get_collection

load_dotenv()

MODELO = "gemini-2.5-flash"
TOP_K = 6

TOM_ESTILO = {
    "Educativo": "Tom didático e informativo, explicando conceitos ou métodos de ensino.",
    "Promocional": "Tom persuasivo com senso de urgência, focado em matrículas e ofertas.",
    "Inspiracional": "Tom emotivo e motivacional, destacando conquistas e potencial dos alunos.",
    "Engajamento": "Tom de pergunta ou desafio, estimulando interação nos comentários.",
    "Depoimento": "Tom de caso real, contando uma história de sucesso em primeira pessoa.",
    "Humor": "Tom leve e descontraído, com memes ou situações do dia adia escolar.",
}

def _get_gemini_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None

def _buscar_contexto(top_k: int = TOP_K) -> str:
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
        docs = resultados.get("documents", [[]])[0]
        return "\n\n".join(docs) if docs else ""
    except Exception:
        return ""

def gerar_legenda(
    image,
    tom: str = "Educativo",
    tema: str = "",
    instrucoes: str = "",
    top_k: int = TOP_K,
) -> dict:
    api_key = _get_gemini_key()
    if not api_key:
        return {"status": "erro", "mensagem": "GEMINI_API_KEY não configurada.", "legendas": [], "hashtags": []}

    contexto = _buscar_contexto(top_k)
    estilo = TOM_ESTILO.get(tom, TOM_ESTILO["Educativo"])

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

    client = genai.Client(api_key=api_key)
    try:
        resposta = client.models.generate_content(
            model=MODELO,
            contents=[prompt, image],
        )
    except Exception as e:
        erro_msg = str(e)
        if "API_KEY" in erro_msg or "API key" in erro_msg:
            msg = "API key inválida. Verifique sua GEMINI_API_KEY."
        elif "SAFETY" in erro_msg or "safety" in erro_msg or "blocked" in erro_msg:
            msg = "A imagem foi bloqueada pelas políticas de segurança do Gemini. Tente outra imagem."
        elif "quota" in erro_msg or "quota" in erro_msg.lower() or "429" in erro_msg:
            msg = "Limite de requisições excedido. Aguarde um momento e tente novamente."
        elif "500" in erro_msg or "internal" in erro_msg.lower():
            msg = "Erro interno do servidor Gemini. Tente novamente."
        else:
            msg = f"Erro ao gerar legendas: {erro_msg[:300]}"
        return {"status": "erro", "mensagem": msg, "legendas": [], "hashtags": []}

    conteudo = resposta.text or ""
    if not conteudo:
        return {"status": "erro", "mensagem": "Gemini retornou resposta vazia.", "legendas": [], "hashtags": []}

    return {
        "status": "ok",
        "conteudo": conteudo,
        "contexto_usado": bool(contexto),
        "tom": tom,
    }
