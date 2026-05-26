"""Módulo de orquestração para processamento e indexação de documentos.
Delega extração para utils/extractors.py e OCR para utils/ocr.py.
"""
import logging
import re
from pathlib import Path

from chromadb import PersistentClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PATH,
    COLLECTION_NAME,
)
from utils.extractors import extrair_arquivo, extrair_texto
from utils.ocr import diagnosticar_ocr

logger = logging.getLogger(__name__)


def sanitizar_id(nome: str) -> str:
    """Sanitiza um nome para uso como ID, removendo caracteres especiais."""
    return re.sub(r'[^a-zA-Z0-9_\-.:]', '_', nome)[:120]


def _get_collection():
    """Obtém ou cria a collection do ChromaDB."""
    CHROMA_PATH.mkdir(exist_ok=True)
    client = PersistentClient(str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
    )


def _backfill_documento_id() -> int:
    """Backfill silencioso de documento_id em chunks legados.

    Chunks criados antes da adição do campo documento_id (commit 8885025)
    não têm esse metadado. Essa função infere o documento_id a partir do
    chunk_id (prefixo antes do _NNN) e atualiza os metadados no ChromaDB.

    Returns:
        int: número de chunks reparados
    """
    try:
        collection = _get_collection()
        total = collection.count()
        if total == 0:
            return 0

        data = collection.get(include=["metadatas"])
        repaired_ids = []
        repaired_mds = []
        changed = False

        for i, md in enumerate(data["metadatas"]):
            if md is None:
                continue
            if md.get("documento_id"):
                continue  # já tem, pula

            chunk_id = data["ids"][i]
            match = re.match(r'^(.+?)(_\d+)?$', chunk_id)
            doc_id = sanitizar_id(match.group(1)) if match else sanitizar_id(chunk_id)
            md["documento_id"] = doc_id
            repaired_ids.append(chunk_id)
            repaired_mds.append(md)
            changed = True

        if changed:
            collection.update(ids=repaired_ids, metadatas=repaired_mds)
            logger.info("Backfill: %d chunks legados receberam documento_id", len(repaired_ids))

        return len(repaired_ids)
    except Exception as e:
        logger.warning("Backfill de documento_id falhou: %s", e)
        return 0


def deletar_do_chromadb(documento_id: str, chave: str = "") -> None:
    """Remove chunks do ChromaDB, com fallback para chave sem documento_id.

    Args:
        documento_id: ID do documento no ChromaDB (pode ser vazio para legados).
        chave: Nome/chave da fonte no session_state (usado no fallback).
    """
    colecao = _get_collection()

    if documento_id:
        try:
            colecao.delete(where={"documento_id": documento_id})
            return
        except Exception as e:
            logger.warning(
                "Erro ao deletar por documento_id '%s': %s", documento_id, e
            )

    # Fallback 1: inferir documento_id a partir da chave
    if chave:
        try:
            inferred = sanitizar_id(chave)
            colecao.delete(where={"documento_id": inferred})
            logger.info(
                "Delete por inferência (chave='%s' → doc_id='%s') OK",
                chave, inferred,
            )
            return
        except Exception as e:
            logger.warning("Fallback por inferência falhou: %s", e)

    # Fallback 2: varredura por metadados
    try:
        data = colecao.get(include=["metadatas"])
        ids_para_remover = []
        for i, md in enumerate(data["metadatas"]):
            chunk_id = data["ids"][i]
            if not md:
                continue
            if md.get("documento_id") and documento_id and md["documento_id"] == documento_id:
                ids_para_remover.append(chunk_id)
            elif chave and md.get("arquivo", "") == chave:
                ids_para_remover.append(chunk_id)
        if ids_para_remover:
            colecao.delete(ids=ids_para_remover)
            logger.info(
                "Fallback 2 deletou %d chunks por varredura", len(ids_para_remover)
            )
    except Exception as e:
        logger.error("Todos os fallbacks falharam ao deletar '%s': %s", chave, e)


def chunk_texto(texto: str) -> list[dict]:
    """Divide texto em chunks para indexação."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.create_documents([texto])
    return [
        {
            "texto": chunk.page_content,
            "metadata": chunk.metadata or {},
        }
        for chunk in chunks
    ]


def salvar_chunks(
    chunks: list[dict],
    documento_id: str = None,
    extra_metadata: dict = None,
) -> int:
    """Salva chunks no ChromaDB e opcionalmente no Firebase."""
    collection = _get_collection()
    ids = []
    textos = []
    metadatas = []
    doc_id = sanitizar_id(documento_id or "doc")

    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_{i}"
        ids.append(chunk_id)
        textos.append(chunk["texto"])
        md = {**chunk["metadata"], "chunk_id": chunk_id}
        if extra_metadata:
            md.update(extra_metadata)
        md["documento_id"] = doc_id
        metadatas.append(md)

    collection.upsert(documents=textos, metadatas=metadatas, ids=ids)

    try:
        from utils.firebase_store import salvar_chunks_firestore
        salvar_chunks_firestore(ids, textos, metadatas)
    except Exception:
        logger.debug("Firebase não disponível para salvar (ignorado)")

    return len(chunks)


def salvar_resumo_documento(documento_id: str, resumo: str):
    """Atualiza o campo 'resumo' em todos os chunks de um documento."""
    collection = _get_collection()
    try:
        resultados = collection.get(where={"documento_id": sanitizar_id(documento_id)})
        if not resultados or not resultados["ids"]:
            return
        novos_metadatas = []
        for md in resultados["metadatas"]:
            md["resumo"] = resumo
            novos_metadatas.append(md)
        collection.update(
            ids=resultados["ids"],
            metadatas=novos_metadatas,
        )
    except Exception as e:
        logger.debug(f"Erro ao salvar resumo no ChromaDB: {e}")





def processar_documento(pdf_bytes: bytes, nome_arquivo: str = None) -> dict:
    """Processa um documento PDF: extrai texto, cria chunks e salva."""
    resultado_extracao = extrair_texto(pdf_bytes)
    
    # Se extrair_texto já retornou erro formatado (ex: subprocesso falhou)
    if resultado_extracao.get("status") == "erro":
        return resultado_extracao
    
    texto = resultado_extracao.get("texto", "")
    paginas = resultado_extracao.get("paginas", 0)
    metodo = resultado_extracao.get("metodo", "desconhecido")

    if not texto.strip():
        msg = f"Nenhum texto extraído do PDF ({paginas} páginas, método: {metodo})."
        if metodo.startswith("erro:"):
            msg += f" Detalhes: {metodo[5:]}"
        elif metodo == "ocr":
            ocr_diag = diagnosticar_ocr()
            msg += f" Diagnóstico OCR: {ocr_diag}"
        return {
            "status": "erro",
            "mensagem": msg,
            "paginas": paginas,
            "metodo": metodo,
        }
    
    chunks = chunk_texto(texto)
    total = salvar_chunks(
        chunks,
        documento_id=nome_arquivo,
        extra_metadata={"fonte": "pdf", "arquivo": nome_arquivo},
    )
    return {
        "status": "ok",
        "total_chunks": total,
        "total_caracteres": len(texto),
        "paginas": paginas,
        "metodo": metodo,
        "texto_completo": texto,
    }


def processar_arquivo(bytes_arquivo: bytes, nome_arquivo: str) -> dict:
    """Processa um arquivo qualquer: extrai texto, cria chunks e salva."""
    resultado = extrair_arquivo(bytes_arquivo, nome_arquivo)
    texto = resultado["texto"]
    paginas = resultado["paginas"]
    metodo = resultado["metodo"]
    
    if "erro" in resultado:
        return {
            "status": "erro",
            "mensagem": resultado["erro"],
            "paginas": 0,
            "metodo": metodo,
        }

    if not texto.strip():
        return {
            "status": "erro",
            "mensagem": f"Nenhum texto extraído ({nome_arquivo}, método: {metodo}).",
            "paginas": paginas,
            "metodo": metodo,
        }
    
    chunks = chunk_texto(texto)
    extensao = Path(nome_arquivo).suffix.lower()
    total = salvar_chunks(
        chunks,
        documento_id=nome_arquivo,
        extra_metadata={"fonte": extensao, "arquivo": nome_arquivo},
    )
    return {
        "status": "ok",
        "total_chunks": total,
        "total_caracteres": len(texto),
        "paginas": paginas,
        "metodo": metodo,
        "texto_completo": texto,
    }
