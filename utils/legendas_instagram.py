"""
Módulo para geração de legendas para Instagram usando Gemini.
"""

import logging

from utils.documentos import _get_collection
from utils.gemini_client import (
    GeminiError,
    GeminiAPIKeyError,
    GeminiSafetyError,
    GeminiQuotaError,
    GeminiDailyQuotaError,
    GeminiServerError,
    get_cliente,
)

logger = logging.getLogger(__name__)

MODELO = "gemini-2.5-flash"
TOP_K = 6

TOM_ESTILO = {
    "Educativo": "Tom didático e informativo, explicando conceitos ou métodos de ensino.",
    "Promocional": "Tom persuasivo com senso de urgência, focado em matrículas e ofertas.",
    "Inspiracional": "Tom emotivo e motivacional, destacando conquistas e potencial dos alunos.",
    "Engajamento": "Tom de pergunta ou desafio, estimulando interação nos comentários.",
    "Depoimento": "Tom de caso real, contando uma história de sucesso em primeira pessoa.",
    "Humor": "Tom leve e descontraído, com memes ou situações do dia a dia escolar.",
}


def _buscar_contexto(top_k: int = TOP_K) -> str:
    """Busca contexto relevante do vector store."""
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
        docs = resultados.get("documents", [[]])
        return "\n\n".join(docs) if docs else ""
    
    except Exception as e:
        logger.warning(f"Erro ao buscar contexto: {e}")
        return ""


def gerar_legenda(
    image,
    tom: str = "Educativo",
    tema: str = "",
    instrucoes: str = "",
    top_k: int = TOP_K,
) -> dict:
    """
    Gera 3 opções de legenda para Instagram com base em uma imagem.
    
    Returns:
        Dicionário com status, conteúdo, contexto_usado e tom.
    """
    if tom not in TOM_ESTILO:
        logger.warning(f"Tom '{tom}' não reconhecido, usando 'Educativo'")
        tom = "Educativo"
    
    try:
        cliente = get_cliente(modelo=MODELO)
        if not cliente.api_key_configured:
            return {
                "status": "erro",
                "mensagem": "GEMINI_API_KEY não configurada.",
                "legendas": [],
                "hashtags": [],
            }
    except GeminiAPIKeyError:
        return {
            "status": "erro",
            "mensagem": "GEMINI_API_KEY não configurada.",
            "legendas": [],
            "hashtags": [],
        }
    
    contexto = _buscar_contexto(top_k)
    estilo = TOM_ESTILO.get(tom, TOM_ESTILO["Educativo"])
    prompt = _construir_prompt(tom, estilo, tema, instrucoes, contexto)
    
    try:
        cliente = get_cliente(modelo=MODELO)
        conteudo = cliente.gerar_com_imagem(
            prompt=prompt,
            imagem=image,
            usar_cache=False,
            temperatura=0.7,
            max_tokens=4096,
        )
        
        if not conteudo:
            return {
                "status": "erro",
                "mensagem": "Gemini retornou resposta vazia.",
                "legendas": [],
                "hashtags": [],
            }
        
        # Remover HTML que o Gemini insiste em gerar
        import re
        conteudo = re.sub(r'<[^>]*>', '', conteudo)
        conteudo = re.sub(r'\n{3,}', '\n\n', conteudo)
        
        return {
            "status": "ok",
            "conteudo": conteudo,
            "contexto_usado": bool(contexto),
            "tom": tom,
        }
    
    except GeminiAPIKeyError:
        return {
            "status": "erro",
            "mensagem": "GEMINI_API_KEY não configurada.",
            "legendas": [],
            "hashtags": [],
        }
    except GeminiSafetyError:
        return {
            "status": "erro",
            "mensagem": "A imagem foi bloqueada pelas políticas de segurança do Gemini. Tente outra imagem.",
            "legendas": [],
            "hashtags": [],
        }
    except GeminiDailyQuotaError:
        return {
            "status": "erro",
            "mensagem": "⚠️ Limite **diário** de requisições excedido. O Google Gemini resetará a cota — você poderá usar o app novamente amanhã.",
            "legendas": [],
            "hashtags": [],
        }
    except GeminiQuotaError:
        return {
            "status": "erro",
            "mensagem": "Limite de requisições excedido. Aguarde um momento e tente novamente.",
            "legendas": [],
            "hashtags": [],
        }
    except GeminiServerError:
        return {
            "status": "erro",
            "mensagem": "Erro interno do servidor Gemini. Tente novamente.",
            "legendas": [],
            "hashtags": [],
        }
    except GeminiError as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao gerar legendas: {e.message[:300]}",
            "legendas": [],
            "hashtags": [],
        }


def _construir_prompt(
    tom: str,
    estilo: str,
    tema: str,
    instrucoes: str,
    contexto: str,
) -> str:
    """Constrói o prompt completo para geração de legendas."""
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
    
    return prompt
