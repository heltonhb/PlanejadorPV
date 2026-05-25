"""Utilitário de reconstrução de fontes — usado na inicialização do app.

Recupera a lista de fontes do ChromaDB (ou Firestore como fallback)
quando o session_state é perdido (reboot/redeploy).
"""

import logging

logger = logging.getLogger(__name__)


def reconstruir_fontes(recarregou: int = 0) -> tuple[dict, int]:
    """Tenta reconstruir documentosc_meta a partir do banco de dados.

    Returns:
        tuple[dict, int]: (documentos_meta, total_fontes)
            documentos_meta: dict chave -> {fonte, nome, chunks, ...}
            total_fontes: número de fontes encontradas
    """
    from utils.documentos import _get_collection as _get_docs_collection
    from utils.firebase_store import carregar_fontes_meta
    from utils.relatorios import resumo_conteudo

    # ── 1ª tentativa: resumo_conteudo() (agrupa por título) ──
    try:
        _rel = resumo_conteudo()
        _fontes_detalhadas = _rel.get("fontes_detalhadas") or []
        if _fontes_detalhadas:
            meta = {}
            for item in _fontes_detalhadas:
                chave = item["titulo"]
                if chave in meta:
                    meta[chave]["chunks"] += item["chunks"]
                    meta[chave]["caracteres"] += item["caracteres"]
                else:
                    meta[chave] = {
                        "fonte": item["fonte"],
                        "nome": item["titulo"],
                        "chunks": item["chunks"],
                        "caracteres": item["caracteres"],
                        "documento_id": item.get("documento_id", ""),
                    }
            # Mescla com metadados extras do Firestore (se disponível)
            try:
                fb_meta = carregar_fontes_meta()
                if fb_meta:
                    for chave, dados in fb_meta.items():
                        if chave in meta:
                            meta[chave].update(dados)
                        else:
                            meta[chave] = dados
            except Exception:
                pass
            logger.info("Fontes reconstruídas via resumo_conteudo: %d", len(meta))
            return meta, len(meta)
    except Exception as e:
        logger.warning("resumo_conteudo falhou: %s", e)

    # ── 2ª tentativa: busca direta na collection ──
    if recarregou > 0:
        try:
            collection = _get_docs_collection()
            data = collection.get(include=["metadatas"])
            if data and data["ids"]:
                meta = {}
                for i, md in enumerate(data["metadatas"]):
                    if md is None:
                        continue
                    titulo = (
                        md.get("arquivo")
                        or md.get("url")
                        or md.get("titulo")
                        or f"documento_{i}"
                    )
                    fonte = md.get("fonte", "desconhecido")
                    if titulo not in meta:
                        meta[titulo] = {
                            "fonte": fonte,
                            "nome": titulo,
                            "chunks": 0,
                            "caracteres": 0,
                            "documento_id": md.get("documento_id", ""),
                        }
                    meta[titulo]["chunks"] += 1
                    meta[titulo]["caracteres"] += len(str(md.get("texto", "")))
                logger.info(
                    "Fontes reconstruídas via busca manual: %d", len(meta)
                )
                return meta, len(meta)
        except Exception as e:
            logger.warning("Busca manual na collection falhou: %s", e)

    # ── 3ª tentativa: só Firestore ──
    try:
        fb_meta = carregar_fontes_meta()
        if fb_meta:
            logger.info(
                "Fontes reconstruídas via Firestore: %d", len(fb_meta)
            )
            return fb_meta, len(fb_meta)
    except Exception:
        pass

    return {}, 0
