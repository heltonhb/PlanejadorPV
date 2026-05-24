import logging

logger = logging.getLogger(__name__)


def init_firebase():
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        logger.warning("firebase-admin não instalado")
        return False

    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        pass

    try:
        import streamlit as st
        cred_dict = dict(st.secrets.get("firebase", {}))
        if not cred_dict:
            logger.warning("Firebase credentials not found in st.secrets['firebase']")
            return False
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        logger.warning("Erro ao inicializar Firebase: %s", e)
        return False


def salvar_chunks_firestore(ids: list[str], textos: list[str], metadatas: list[dict]) -> int:
    if not init_firebase():
        return 0
    from firebase_admin import firestore
    db = firestore.client()
    saved = 0
    for i, doc_id in enumerate(ids):
        db.collection("chunks").document(doc_id).set({
            "texto": textos[i],
            "metadata": metadatas[i],
        })
        saved += 1
    return saved


def recarregar_chunks() -> int:
    from utils.documentos import _get_collection
    collection = _get_collection()

    if not init_firebase():
        logger.warning("Firebase não disponível para recarregar")
        return 0

    from firebase_admin import firestore
    db = firestore.client()
    docs = db.collection("chunks").stream()
    ids, textos, metadatas = [], [], []
    for doc in docs:
        data = doc.to_dict()
        ids.append(doc.id)
        textos.append(data.get("texto", ""))
        metadatas.append(data.get("metadata", {}))

    if not ids:
        return 0

    collection.upsert(documents=textos, metadatas=metadatas, ids=ids)
    logger.info("Recarregados %d chunks do Firestore", len(ids))
    return len(ids)


def limpar_firestore():
    if not init_firebase():
        return
    from firebase_admin import firestore
    db = firestore.client()
    # Limpar chunks
    batch = db.batch()
    docs = db.collection("chunks").list_documents()
    for doc in docs:
        batch.delete(doc)
    batch.commit()
    # Limpar metadados de fontes
    batch2 = db.batch()
    meta_docs = db.collection("fontes_meta").list_documents()
    for doc in meta_docs:
        batch2.delete(doc)
    batch2.commit()


def salvar_fonte_meta(chave: str, meta: dict) -> bool:
    """Salva metadados de uma fonte no Firestore para persistência."""
    if not init_firebase():
        return False
    try:
        from firebase_admin import firestore
        db = firestore.client()
        # Sanitizar a chave para usar como document ID
        import re
        doc_id = re.sub(r'[^a-zA-Z0-9_\-.:]+', '_', chave)[:200]
        db.collection("fontes_meta").document(doc_id).set({
            "chave_original": chave,
            "meta": meta,
        })
        return True
    except Exception as e:
        logger.debug("Erro ao salvar fonte_meta no Firestore: %s", e)
        return False


def remover_fonte_meta(chave: str) -> bool:
    """Remove metadados de uma fonte do Firestore."""
    if not init_firebase():
        return False
    try:
        from firebase_admin import firestore
        import re
        db = firestore.client()
        doc_id = re.sub(r'[^a-zA-Z0-9_\-.:]+', '_', chave)[:200]
        db.collection("fontes_meta").document(doc_id).delete()
        return True
    except Exception as e:
        logger.debug("Erro ao remover fonte_meta do Firestore: %s", e)
        return False


def carregar_fontes_meta() -> dict[str, dict]:
    """Carrega todos os metadados de fontes do Firestore.

    Returns:
        dict mapeando chave_original -> meta dict
    """
    if not init_firebase():
        return {}
    try:
        from firebase_admin import firestore
        db = firestore.client()
        docs = db.collection("fontes_meta").stream()
        resultado = {}
        for doc in docs:
            data = doc.to_dict()
            chave = data.get("chave_original", doc.id)
            meta = data.get("meta", {})
            resultado[chave] = meta
        return resultado
    except Exception as e:
        logger.debug("Erro ao carregar fontes_meta do Firestore: %s", e)
        return {}

