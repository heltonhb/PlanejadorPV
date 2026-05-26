"""
Módulo para geração de calendários editoriais usando Gemini.
"""

import calendar
import logging

from utils.documentos import _get_collection
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.constants import MESES
from utils.helpers import sanitizar_html, tratar_erro_gemini

logger = logging.getLogger(__name__)


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


def gerar_calendario(mes: str, ano: int) -> dict:
    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        if not cliente.api_key_configured:
            return {"status": "erro", "mensagem": "GEMINI_API_KEY não configurada.", "conteudo": ""}
    except GeminiAPIKeyError:
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

    try:
        conteudo = cliente.gerar_texto(
            prompt=prompt,
            usar_cache=True,
            temperatura=0.7,
            max_tokens=4096,
        )
        if not conteudo:
            return {
                "status": "erro",
                "mensagem": "Gemini retornou uma resposta vazia. Tente novamente.",
                "conteudo": "",
            }
        conteudo = sanitizar_html(conteudo)
        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
        }

    except GeminiError as e:
        logger.error(f"Erro Gemini em gerar_calendario: {e}")
        return {
            "status": "erro",
            "mensagem": tratar_erro_gemini(e),
            "conteudo": "",
        }
