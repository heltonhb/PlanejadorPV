import logging

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
    from utils.documentos import _get_collection
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
        unique_key = f"{fonte}::{titulo}"
        if unique_key not in agrupado[fonte]:
            agrupado[fonte][unique_key] = {
                "titulo": titulo,
                "filhos": 0,
                "caracteres": 0,
                "documento_id": documento_id,
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
            })

    return {
        "total_chunks": total_chunks,
        "total_caracteres": sum(p["caracteres"] for p in por_fonte.values()),
        "por_fonte": por_fonte,
        "fontes_detalhadas": sorted(fontes_list, key=lambda x: (x["fonte"], x["titulo"])),
    }
