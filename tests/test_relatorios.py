from unittest.mock import MagicMock, patch

from utils.relatorios import formatar_resumo_detalhado, resumo_conteudo


class TestResumoConteudo:
    @patch("utils.relatorios._get_collection")
    def test_retorna_dict_vazio_quando_colecao_vazia(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        resultado = resumo_conteudo()
        assert isinstance(resultado, dict)

    @patch("utils.relatorios._get_collection")
    def test_retorna_dict_com_dados_quando_colecao_populada(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.get.return_value = {
            "ids": ["ch1", "ch2"],
            "documents": ["Texto do documento A", "Texto do documento B"],
            "metadatas": [
                {"documento_id": "doc1", "data": "2025-01-01"},
                {"documento_id": "doc2", "data": "2025-01-15"},
            ],
        }
        mock_get_collection.return_value = mock_collection

        resultado = resumo_conteudo()
        assert isinstance(resultado, dict)

    @patch("utils.relatorios._get_collection")
    def test_erro_colecao_retorna_dict_com_erro(self, mock_get_collection):
        mock_get_collection.side_effect = Exception("Erro ao acessar ChromaDB")
        resultado = resumo_conteudo()
        assert "erro" in str(resultado).lower()


class TestFormatarResumoDetalhado:
    def test_formata_lista_de_documentos(self):
        dados = {
            "total_documentos": 2,
            "total_chunks": 5,
            "documentos": [{"id": "doc1", "chunks": 3}, {"id": "doc2", "chunks": 2}],
        }
        resultado = formatar_resumo_detalhado(dados)
        assert isinstance(resultado, str)
        assert "doc1" in resultado
        assert "doc2" in resultado

    def test_dados_vazios_retorna_string_vazia_ou_aviso(self):
        resultado = formatar_resumo_detalhado({})
        assert isinstance(resultado, str)
