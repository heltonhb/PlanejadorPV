"""
Módulo para geração de campanhas de marketing usando Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import (
    GeminiError,
    GeminiAPIKeyError,
    GeminiQuotaError,
    GeminiServerError,
    GeminiSafetyError,
    get_cliente,
)

logger = logging.getLogger(__name__)

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
        cliente = get_cliente(modelo=MODELO)
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
        cliente = get_cliente(modelo=MODELO)
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
        
        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
        }
    
    except GeminiAPIKeyError:
        return {
            "status": "erro",
            "mensagem": "Chave da API Gemini inválida ou não encontrada.",
            "conteudo": "",
        }
    except GeminiQuotaError:
        return {
            "status": "erro",
            "mensagem": "Limite de requisições excedido. Aguarde alguns minutos e tente novamente.",
            "conteudo": "",
        }
    except GeminiServerError:
        return {
            "status": "erro",
            "mensagem": "Servidor do Gemini temporariamente indisponível. Tente novamente em alguns instantes.",
            "conteudo": "",
        }
    except GeminiSafetyError:
        return {
            "status": "erro",
            "mensagem": "O conteúdo foi bloqueado pelos filtros de segurança do Gemini. Tente reformular a solicitação.",
            "conteudo": "",
        }
    except GeminiError as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao comunicar com o Gemini: {e.message[:200]}",
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
        f"\nFormato da resposta (use Markdown):\n\n"
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
    
    prompt += (
        f"\n### Cronograma\n"
        f"- **Semana 1**: [ação]\n"
        f"- **Semana 2**: [ação]\n"
        f"- **Semana 3**: [ação]\n\n"
        f"### Investimento Sugerido\n"
        f"[divisão do orçamento e estimativa de investimento]\n\n"
        f"### Métricas de Sucesso\n"
        f"[como medir se a campanha deu certo]\n\n"
        f"Regras:\n"
        f"1. Seja específico e acionável — o usuário é um franqueado.\n"
        f"2. Adapte a linguagem e os exemplos ao público-alvo informado.\n"
        f"3. Se houver dados dos documentos, use-as.\n"
        f"4. Mantenha tom profissional mas acessível."
    )
    
    return prompt
