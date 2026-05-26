"""
Módulo para geração de campanhas de marketing usando Gemini.
"""

import logging
from typing import Optional

from utils.documentos import _get_collection
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.helpers import sanitizar_html, tratar_erro_gemini, parse_duration_days
from utils.prompts import PERSONA_CONSULTOR, formatar_contexto, regras_padrao

logger = logging.getLogger(__name__)


def _buscar_contexto_campanha(top_k: int = 8) -> str:
    """Busca contexto relevante da base vetorial."""
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return ""
        consulta = "Ensina Mais Turma da Monica Tatuapé marketing campanha"
        resultados = collection.query(
            query_texts=[consulta], n_results=min(top_k, count),
            include=["documents"],
        )
        docs = resultados.get("documents", [[]])
        return "\n\n".join(docs[0]) if docs and docs[0] else ""
    except Exception as e:
        logger.warning(f"Erro ao buscar contexto campanha: {e}")
        return ""


def _cronograma_conforme_dias(dias: int) -> str:
    """Gera template de cronograma de acordo com a duração."""
    if dias <= 8:
        return (
            "### Cronograma ({dias} dias)\n"
            "- **Dias 1-2**: [ação]\n"
            "- **Dias 3-5**: [ação]\n"
            "- **Dias 6-{dias}**: [ação]"
        ).format(dias=dias)
    elif dias <= 16:
        return (
            "### Cronograma ({dias} dias)\n"
            "- **Semana 1**: [ação]\n"
            "- **Semana 2**: [ação]"
        ).format(dias=dias)
    elif dias <= 24:
        return (
            "### Cronograma ({dias} dias)\n"
            "- **Semana 1**: [ação]\n"
            "- **Semana 2**: [ação]\n"
            "- **Semana 3**: [ação]"
        ).format(dias=dias)
    elif dias <= 35:
        return (
            "### Cronograma ({dias} dias)\n"
            "- **Semana 1**: [ação]\n"
            "- **Semana 2**: [ação]\n"
            "- **Semana 3**: [ação]\n"
            "- **Semana 4**: [ação]"
        ).format(dias=dias)
    else:
        return (
            "### Cronograma ({dias} dias)\n"
            "- **Fase 1 (Início)**: [ação]\n"
            "- **Fase 2 (Aquecimento)**: [ação]\n"
            "- **Fase 3 (Conversão)**: [ação]\n"
            "- **Fase 4 (Fechamento)**: [ação]"
        ).format(dias=dias)


def gerar_campanha(
    objetivo: str,
    publico: str,
    servico: str,
    nome: str = "",
    canais: Optional[list] = None,
    orcamento: float = 0.0,
    datas: str = "",
) -> dict:
    """Gera uma campanha de marketing completa."""
    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        if not cliente.api_key_configured:
            return {
                "status": "erro",
                "mensagem": "GEMINI_API_KEY não configurada.",
                "conteudo": "",
            }
    except GeminiAPIKeyError:
        return {
            "status": "erro",
            "mensagem": "GEMINI_API_KEY não configurada.",
            "conteudo": "",
        }

    contexto = _buscar_contexto_campanha()
    prompt = _construir_prompt(
        objetivo=objetivo,
        publico=publico,
        servico=servico,
        nome=nome,
        canais=canais or [],
        orcamento=orcamento,
        datas=datas,
        contexto=contexto,
    )

    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
        conteudo = cliente.gerar_texto(
            prompt=prompt,
            system_instruction=PERSONA_CONSULTOR,
            usar_cache=True,
            temperatura=0.7,
            max_tokens=4096,
        )

        if not conteudo:
            return {
                "status": "erro",
                "mensagem": "Gemini retornou resposta vazia. Tente novamente.",
                "conteudo": "",
            }

        conteudo = sanitizar_html(conteudo)

        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
        }

    except GeminiError as e:
        return {
            "status": "erro",
            "mensagem": tratar_erro_gemini(e),
            "conteudo": "",
        }


def _construir_prompt(
    objetivo: str,
    publico: str,
    servico: str,
    nome: str,
    canais: list,
    orcamento: float,
    datas: str,
    contexto: str,
) -> str:
    """Constrói o prompt de usuário para geração de campanhas."""
    linhas = [
        "Crie uma campanha de marketing completa com base nas informações abaixo.",
        "",
        "=== DADOS DA CAMPANHA ===",
        f"Objetivo: {objetivo}",
        f"Público-alvo: {publico}",
        f"Serviço: {servico}",
        f"Franquia: Ensina Mais Turma da Mônica — Unidade Tatuapé, SP",
    ]

    if nome:
        linhas.append(f"Nome sugerido: {nome}")
    if canais:
        linhas.append(f"Canais: {', '.join(canais)}")
    if orcamento > 0:
        linhas.append(f"Orçamento: R$ {orcamento:,.2f}")
    if datas:
        linhas.append(f"Período: {datas}")

    ctx = formatar_contexto(contexto)
    if ctx:
        linhas.append("")
        linhas.append(ctx)

    # Duração para cronograma
    dias = parse_duration_days(datas)
    cronograma_template = _cronograma_conforme_dias(dias)

    linhas += [
        "",
        "FORMATO DA RESPOSTA (Markdown — NÃO use HTML):",
        "",
        "## Nome da Campanha",
        "[nome da campanha]",
        "",
        "### Descrição",
        "[descrição da campanha]",
        "",
        "### Canais e Ações",
    ]

    if canais:
        for c in canais:
            linhas.append(f"- **{c}**: [ações específicas para {c}]")
    else:
        linhas += [
            "- **Instagram**: [ideias de posts, stories ou reels]",
            "- **WhatsApp**: [texto ou roteiro para disparo]",
            "- **Material Impresso**: [ideia de flyer, cartaz ou panfleto]",
        ]

    linhas += [
        "",
        cronograma_template,
        "",
        "### Investimento Sugerido",
        "[divisão do orçamento e estimativa de investimento]",
        "",
        "### Métricas de Sucesso",
        "[como medir se a campanha deu certo]",
        "",
        regras_padrao(
            "Adapte a linguagem ao público-alvo informado.",
            "Se houver contexto dos documentos, use-o para personalizar.",
        ),
    ]

    return "\n".join(linhas)
