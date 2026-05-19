import os
import calendar

from dotenv import load_dotenv
from google import genai

from utils.documentos import _get_collection

load_dotenv()

MODELO = "gemini-2.5-flash"

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _buscar_contexto_calendario(mes: str, top_k: int = 10) -> str:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return ""
    consulta = f"marketing para {mes} franquia educacional Ensina Mais Tatuapé"
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


def gerar_calendario(mes: str, ano: int) -> dict:
    api_key = _get_gemini_key()
    if not api_key:
        return {"status": "erro", "mensagem": "GEMINI_API_KEY não configurada.", "conteudo": ""}

    contexto = _buscar_contexto_calendario(mes)
    dias_no_mes = calendar.monthrange(ano, MESES.index(mes) + 1)[1]

    prompt = (
        f"Você é um consultor de marketing especializado em franquias educacionais "
        f"da rede Ensina Mais Turma da Mônica. Crie um plano de ações de marketing "
        f"para {mes} de {ano} ({dias_no_mes} dias).\n\n"
        f"Considere:\n"
        f"- Franquia: Ensina Mais Turma da Mônica\n"
        f"- Unidade: Tatuapé - SP\n"
        f"- Público: Fundamental I e II\n"
        f"- Serviços: apoio escolar (português e matemática) e tecnologia "
        f"(programação e robótica)\n"
    )
    if contexto:
        prompt += (
            f"- Contexto extraído dos documentos da franquia:\n{contexto}\n\n"
        )
    prompt += (
        f"Formato da resposta (use Markdown):\n\n"
        f"## {mes} — Visão Geral\n"
        f"[Breve descrição do foco do mês]\n\n"
    )
    for s in range(1, 6):
        prompt += (
            f"### Semana {s}\n"
        )
    prompt += (
        f"**Dica extra para o mês:** [dica rápida]\n\n"
        f"Regras:\n"
        f"1. Cada semana deve ter 2 a 3 ações específicas e acionáveis.\n"
        f"2. Para cada ação, indique o canal (Instagram, WhatsApp, Material Impresso).\n"
        f"3. Use emojis para destacar cada ação.\n"
        f"4. Seja prático — o usuário é um franqueado que precisa executar.\n"
        f"5. Preencha APENAS as semanas que existem em {mes} (até {dias_no_mes} dias).\n"
        f"6. Se houver informações dos documentos, use-as para personalizar.\n"
        f"7. Se não houver documentos carregados, use seu conhecimento geral "
        f"sobre o calendário escolar brasileiro."
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
