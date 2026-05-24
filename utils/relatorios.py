import logging
from utils.documentos import _get_collection

logger = logging.getLogger(__name__)

ICONES_FONTE = {
    "pdf": "📄",
    "url": "🔗",
    "html": "🌐",
    "instagram": "📷",
    "texto": "📝",
    "planilha": "📊",
}


def resumo_conteudo() -> dict:
    try:
        collection = _get_collection()

        total_chunks = collection.count()
        if total_chunks == 0:
            return {"total_chunks": 0, "total_caracteres": 0, "por_fonte": {}, "fontes_detalhadas": []}

        data = collection.get(include=["documents", "metadatas"])

        por_fonte = {}
        agrupado = {}

        for i, doc_id in enumerate(data["ids"]):
            md = data["metadatas"][i]
            fonte = md.get("fonte", "desconhecido")
            doc_len = len(data["documents"][i]) if data["documents"][i] else 0

            if fonte not in por_fonte:
                por_fonte[fonte] = {"chunks": 0, "caracteres": 0}
                agrupado[fonte] = {}

            por_fonte[fonte]["chunks"] += 1
            por_fonte[fonte]["caracteres"] += doc_len

            titulo = (
                md.get("arquivo")
                or md.get("url")
                or md.get("perfil")
                or md.get("titulo")
                or "desconhecido"
            )
            documento_id = md.get("documento_id")
            resumo = md.get("resumo", "")
            unique_key = f"{fonte}::{titulo}"
            if unique_key not in agrupado[fonte]:
                agrupado[fonte][unique_key] = {
                    "titulo": titulo,
                    "filhos": 0,
                    "caracteres": 0,
                    "documento_id": documento_id,
                    "primeiro_trecho": data["documents"][i] if data["documents"][i] else "",
                    "resumo": resumo,
                }
            agrupado[fonte][unique_key]["filhos"] += 1
            agrupado[fonte][unique_key]["caracteres"] += doc_len

        fontes_list = []
        for fonte, items in agrupado.items():
            for key, info in items.items():
                fontes_list.append({
                    "fonte": fonte,
                    "icone": ICONES_FONTE.get(fonte, "📄"),
                    "titulo": info["titulo"],
                    "chunks": info["filhos"],
                    "caracteres": info["caracteres"],
                    "documento_id": info["documento_id"],
                    "preview": info.get("primeiro_trecho", "")[:250],
                    "resumo": info.get("resumo", ""),
                })

        return {
            "total_chunks": total_chunks,
            "total_caracteres": sum(p["caracteres"] for p in por_fonte.values()),
            "por_fonte": por_fonte,
            "fontes_detalhadas": sorted(fontes_list, key=lambda x: (x["fonte"], x["titulo"])),
        }
    except Exception as e:
        logger.error(f"Erro ao obter resumo do conteúdo: {e}")
        return {
            "status": "erro",
            "mensagem": f"Erro ao acessar base de conhecimento: {str(e)}",
            "total_chunks": 0,
            "total_caracteres": 0,
            "por_fonte": {},
            "fontes_detalhadas": []
        }


def formatar_resumo_detalhado(dados: dict) -> str:
    """
    Formata em markdown a lista de documentos para relatório.
    """
    if not dados:
        return "Nenhum documento cadastrado."
    
    resumo = []
    total_docs = dados.get("total_documentos", 0)
    total_chunks = dados.get("total_chunks", 0)
    resumo.append(f"### Relatório Consolidado de Documentos")
    resumo.append(f"- **Total de Documentos:** {total_docs}")
    resumo.append(f"- **Total de Trechos (chunks):** {total_chunks}\n")
    
    docs = dados.get("documentos", [])
    if docs:
        resumo.append("| ID do Documento | Trechos |")
        resumo.append("| --- | --- |")
        for doc in docs:
            doc_id = doc.get("id", "desconhecido")
            chunks = doc.get("chunks", 0)
            resumo.append(f"| {doc_id} | {chunks} |")
    else:
        resumo.append("Nenhum detalhe de documento disponível.")
        
    return "\n".join(resumo)
