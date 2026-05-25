import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    firebase_admin = None
    credentials = None
    firestore = None

from utils.documentos import _get_collection

logger = logging.getLogger(__name__)


def _diagnosticar_chave_firebase() -> str:
    """Diagnostica problemas com a chave do Firebase."""
    try:
        import streamlit as st
        cred_dict = dict(st.secrets.get("firebase", {}))
        if not cred_dict:
            return "Firebase não configurado em st.secrets['firebase']"
        pk = cred_dict.get("private_key", "")
        if not pk:
            return "private_key ausente nas credenciais"
        if "BEGIN PRIVATE KEY" not in pk:
            return "private_key não está em formato PEM"
        # Verificar com OpenSSL
        import subprocess, tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(pk)
            pem_path = f.name
        r = subprocess.run(['openssl', 'pkey', '-in', pem_path, '-check'],
                          capture_output=True, text=True, timeout=5)
        os.unlink(pem_path)
        if r.returncode != 0:
            stderr = r.stderr[:200]
            if "p not prime" in stderr:
                return ("❌ Chave privada CORROMPIDA! Os parâmetros RSA são inválidos. "
                        "Isso acontece quando o JSON de serviço é copiado incorretamente "
                        "para o arquivo .streamlit/secrets.toml.\n\n"
                        "**Solução:** Vá em https://console.cloud.google.com/apis/credentials, "
                        "gere uma nova chave para a service account, copie o JSON exato "
                        "(sem modificar quebras de linha) e atualize os secrets.")
            return f"❌ Chave inválida: {stderr}"
        return "✅ Chave válida"
    except Exception as e:
        return f"Erro ao diagnosticar: {e}"


def init_firebase():
    if firebase_admin is None or credentials is None:
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
    db = firestore.client()
    # Usar batch para reduzir de N chamadas para 1
    batch = db.batch()
    for i, doc_id in enumerate(ids):
        doc_ref = db.collection("chunks").document(doc_id)
        batch.set(doc_ref, {
            "texto": textos[i],
            "metadata": metadatas[i],
        })
    batch.commit()
    logger.info("Salvos %d chunks no Firestore (batch)", len(ids))
    return len(ids)


def recarregar_chunks() -> int:
    collection = _get_collection()

    if not init_firebase():
        logger.warning("Firebase não disponível para recarregar")
        return 0

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


def sincronizar_chromadb_para_firestore() -> int:
    """Sincroniza chunks existentes no ChromaDB para o Firestore.
    
    Útil quando o Firebase foi configurado depois de já existirem dados
    no ChromaDB local — migra tudo para o Firestore de uma vez.
    """
    from utils.documentos import _get_collection
    collection = _get_collection()
    
    total = collection.count()
    if total == 0:
        logger.info("ChromaDB vazio, nada a sincronizar")
        return 0
    
    data = collection.get(include=["documents", "metadatas"])
    ids = data["ids"]
    textos = data["documents"]
    metadatas = data["metadatas"]
    
    saved = salvar_chunks_firestore(ids, textos, metadatas)
    logger.info("Sincronizados %d chunks do ChromaDB para Firestore", saved)
    return saved


def limpar_firestore():
    if not init_firebase():
        return
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

