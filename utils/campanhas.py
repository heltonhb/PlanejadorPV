"""
Módulo para geração de campanhas de marketing usando Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import GeminiError, GeminiAPIKeyError, get_cliente
from utils.config import MODELO_GEMINI
from utils.helpers import sanitizar_html, tratar_erro_gemini, parse_duration_days

logger = logging.getLogger(__name__)


def _buscar_contexto_campanha(top_k: int = 8) -> str:
    """Busca contexto relevante do vector store para personalizar a campanha."""
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return ""

        consulta = "marketing campanhas franquia educacional Ensina Mais Tatuapé"
        resultados = collection.query(
            query_texts=[consulta],
            n_results=min(top_k, count),
            include=["documents"],
        )
        docs = resultados.get("documents", [[]])
        if docs and docs[0]:
            return "\n\n".join(docs[0])
        return ""

    except Exception as e:
        logger.warning(f"Erro ao buscar contexto: {e}")
        return ""


def gerar_campanha(
    objetivo: str,
    publico: str,
    servico: str,
    nome: str = "",
    canais: list = None,
    orcamento: float = 0.0,
    datas: str = "",
) -> dict:
    """
    Gera uma campanha de marketing completa.

    Returns:
        Dicionário com status, conteúdo, contexto_usado e mensagem de erro (se houver).
    """
    canais = canais or []

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
        canais=canais,
        orcamento=orcamento,
        datas=datas,
        contexto=contexto,
    )

    try:
        cliente = get_cliente(modelo=MODELO_GEMINI)
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
    """Constrói o prompt completo para geração de campanhas."""
    prompt = (
        f"Crie uma campanha de marketing completa para:\n\n"
        f"Franquia: Ensina Mais Turma da Mônica\n"
        f"Unidade: Tatuapé - SP\n"
        f"Objetivo: {objetivo}\n"
        f"Público-alvo: {publico}\n"
        f"Serviço: {servico}\n"
    )

    if nome:
        prompt += f"Nome sugerido pelo usuário: {nome}\n"

    if canais:
        prompt += f"Canais preferenciais: {', '.join(canais)}\n"

    if orcamento > 0:
        prompt += f"Orçamento disponível: R$ {orcamento:,.2f}\n"

    if datas:
        prompt += f"Período/Datas planejado: {datas}\n"

    if contexto:
        prompt += (
            f"\nUse as informações dos documentos abaixo para personalizar:\n"
            f"{contexto}\n\n"
        )

    prompt += (
        f"\nFormato da resposta (use SOMENTE Markdown, NÃO use HTML):\n\n"
        f"## Nome da Campanha\n"
        f"[nome da campanha]\n\n"
        f"### Descrição\n"
        f"[descrição da campanha]\n\n"
        f"### Canais e Ações\n"
    )

    if canais:
        for c in canais:
            prompt += f"- **{c}**: [ações específicas para o canal {c}]\n"
    else:
        prompt += (
            f"- **Instagram**: [ideias de posts, stories ou reels]\n"
            f"- **WhatsApp**: [texto ou roteiro para disparo]\n"
            f"- **Material Impresso**: [ideia de flyer, cartaz ou panfleto]\n"
        )

    dias = parse_duration_days(datas)

    if dias <= 8:
        cronograma_template = (
            f"### Cronograma ({dias} dias)\n"
            f"- **Dias 1-2**: [ação]\n"
            f"- **Dias 3-5**: [ação]\n"
            f"- **Dias 6-{dias}**: [ação]"
        )
    elif dias <= 16:
        cronograma_template = (
            f"### Cronograma ({dias} dias)\n"
            f"- **Semana 1**: [ação]\n"
            f"- **Semana 2**: [ação]"
        )
    elif dias <= 24:
        cronograma_template = (
            f"### Cronograma ({dias} dias)\n"
            f"- **Semana 1**: [ação]\n"
            f"- **Semana 2**: [ação]\n"
            f"- **Semana 3**: [ação]"
        )
    elif dias <= 35:
        cronograma_template = (
            f"### Cronograma ({dias} dias)\n"
            f"- **Semana 1**: [ação]\n"
            f"- **Semana 2**: [ação]\n"
            f"- **Semana 3**: [ação]\n"
            f"- **Semana 4**: [ação]"
        )
    else:
        cronograma_template = (
            f"### Cronograma ({dias} dias)\n"
            f"- **Fase 1 (Início)**: [ação]\n"
            f"- **Fase 2 (Aquecimento)**: [ação]\n"
            f"- **Fase 3 (Conversão)**: [ação]\n"
            f"- **Fase 4 (Fechamento)**: [ação]"
        )

    prompt += (
        f"\n{cronograma_template}\n\n"
        f"### Investimento Sugerido\n"
        f"[divisão do orçamento e estimativa de investimento]\n\n"
        f"### Métricas de Sucesso\n"
        f"[como medir se a campanha deu certo]\n\n"
        f"Regras:\n"
        f"1. Seja específico e acionável — o usuário é um franqueado.\n"
        f"2. Adapte a linguagem e os exemplos ao público-alvo informado.\n"
        f"3. Se houver dados dos documentos, use-as.\n"
        f"4. USE SOMENTE Markdown. NÃO use tags HTML como <div>, <span>, <style>.\n"
        f"5. Mantenha tom profissional mas acessível."
    )

    return prompt
