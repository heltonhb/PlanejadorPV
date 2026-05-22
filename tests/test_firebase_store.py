from unittest.mock import MagicMock, patch

from utils.firebase_store import (
    init_firebase,
    limpar_firestore,
    recarregar_chunks,
    salvar_chunks_firestore,
)


class TestInitFirebase:
    @patch("utils.firebase_store.firebase_admin.get_app")
    def test_retorna_true_quando_ja_inicializado(self, mock_get_app):
        mock_get_app.return_value = MagicMock()
        resultado = init_firebase()
        assert resultado is True


class TestSalvarChunksFirestore:
    @patch("utils.firebase_store.init_firebase")
    @patch("utils.firebase_store.firestore")
    def test_init_falha_nao_salva(self, mock_firestore, mock_init):
        mock_init.return_value = False
        chunks = [{"texto": "teste", "metadata": {}}]
        resultado = salvar_chunks_firestore(chunks, "doc")
        assert resultado is None or resultado is False


class TestRecarregarChunks:
    @patch("utils.firebase_store.init_firebase")
    @patch("utils.firebase_store._get_collection")
    @patch("utils.firebase_store.firestore")
    def test_carrega_chunks_do_firestore(
        self, mock_firestore, mock_get_collection, mock_init
    ):
        mock_init.return_value = True
        mock_db = MagicMock()
        mock_firestore.client.return_value = mock_db
        doc_snapshot = MagicMock()
        doc_snapshot.to_dict.return_value = {"texto": "conteúdo", "metadata": {"doc_id": "fire_doc"}}
        collection_snapshot = MagicMock()
        collection_snapshot.stream.return_value = [doc_snapshot]
        mock_db.collection.return_value = collection_snapshot

        mock_chroma_collection = MagicMock()
        mock_get_collection.return_value = mock_chroma_collection

        recarregar_chunks()
        mock_chroma_collection.upsert.assert_called()


class TestLimparFirestore:
    @patch("utils.firebase_store.init_firebase")
    @patch("utils.firebase_store.firestore")
    def test_limpa_colecao_especifica(self, mock_firestore, mock_init):
        mock_init.return_value = True
        mock_db = MagicMock()
        mock_firestore.client.return_value = mock_db
        doc_snapshot = MagicMock()
        doc_snapshot.id = "doc_a"
        collection_snapshot = MagicMock()
        collection_snapshot.stream.return_value = [doc_snapshot]
        mock_db.collection.return_value = collection_snapshot

        limpar_firestore("testes")
        doc_snapshot.reference.delete.assert_called()
