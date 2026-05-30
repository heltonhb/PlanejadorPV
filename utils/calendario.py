"""
Módulo para geração de calendários editoriais usando Hermes Operator.
"""

import calendar
import logging

from utils.documentos import _get_collection
from utils.hermes_operator_client import get_cliente_hermes
from utils.constants import MESES
from utils.helpers import sanitizar_html, tratar_erro_ia
from utils.prompts import PERSONA_CONSULTOR, formatar_contexto, FRANQUIA_INFO

logger = logging.getLogger(__name__)


def _buscar_contexto_calendario(mes: str, top_k: int = 10) -> str:
    """Busca chunks relevantes da base vetorial para personalizar o calendário."""
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
    hermes = get_cliente_hermes()
    if not hermes.disponivel:
        return {"status": "erro", "mensagem": "Chave do Hermes Operator não configurada.", "conteudo": ""}

    contexto = _buscar_contexto_calendario(mes)
    dias_no_mes = calendar.monthrange(ano, MESES.index(mes) + 1)[1]

    prompt = _construir_prompt(mes, ano, dias_no_mes, contexto)

    try:
        conteudo = hermes.gerar_texto(
            prompt=prompt,
            system_prompt=PERSONA_CONSULTOR,
            temperatura=0.7,
            max_tokens=4096,
        )
        if not conteudo:
            return {
                "status": "erro",
                "mensagem": "Hermes Operator retornou uma resposta vazia. Tente novamente.",
                "conteudo": "",
            }
        conteudo = sanitizar_html(conteudo)
        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
        }

    except RuntimeError as e:
        logger.error(f"Erro Hermes em gerar_calendario: {e}")
        return {
            "status": "erro",
            "mensagem": tratar_erro_ia(e),
            "conteudo": "",
        }


def _construir_prompt(mes: str, ano: int, dias_no_mes: int, contexto: str) -> str:
    """Constrói o prompt de usuário para geração do calendário editorial."""
    linhas = [
        f"Crie um plano de ações de marketing para {mes} de {ano} ({dias_no_mes} dias).",
        "",
        "INFORMAÇÕES DA FRANQUIA:",
        FRANQUIA_INFO,
    ]

    ctx = formatar_contexto(contexto)
    if ctx:
        linhas.append(ctx)

    linhas += [
        "FORMATO DA RESPOSTA (use Markdown — NÃO use HTML):",
        "",
        f"## {mes} — Visão Geral",
        "[Breve descrição do foco do mês]",
        "",
    ]
    for s in range(1, 6):
        linhas.append(f"### Semana {s}")

    linhas += [
        "",
        "**Dica extra para o mês:** [dica rápida]",
        "",
        "REGRAS:",
        "1. Cada semana deve ter 2 a 3 ações específicas e acionáveis.",
        "2. Para cada ação, indique o canal (Instagram, WhatsApp, Material Impresso).",
        "3. Use emojis para destacar cada ação.",
        f"4. Preencha APENAS as semanas que existem em {mes} (até {dias_no_mes} dias).",
        "5. Se houver contexto dos documentos, use-o para personalizar as ações.",
        "6. Se não houver contexto, use seu conhecimento geral sobre o calendário escolar brasileiro.",
        "7. NÃO use tags HTML (<div>, <span>, <style>, etc.). Apenas Markdown.",
    ]

    return "\n".join(linhas)
