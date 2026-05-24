from unittest.mock import MagicMock, patch

from utils.legendas_instagram import gerar_legenda


class TestGerarLegenda:
    @patch("utils.legendas_instagram._get_collection")
    @patch("google.genai.Client")
    def test_retorna_dict_com_legenda(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "🌟 Legenda incrível para o post!\n\n#hashtag1 #hashtag2"
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_legenda(
            image=b"fake_image_bytes",
            tom="Inspiracional",
            tema="motivacional",
        )
        assert isinstance(resultado, dict)
        assert "conteudo" in resultado
        assert len(resultado["conteudo"]) > 0

    @patch("utils.legendas_instagram._get_collection")
    @patch("google.genai.Client")
    def test_sem_colecao_ignora_contexto(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "Legenda sem contexto."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_legenda(
            image=b"fake_image_bytes",
            tom="Humor",
            tema="cotidiano",
        )
        assert isinstance(resultado, dict)
        assert "conteudo" in resultado

    @patch("utils.legendas_instagram._get_collection")
    @patch("google.genai.Client")
    def test_erro_gemini_retorna_erro(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.models.generate_content.side_effect = Exception("Erro Gemini")

        resultado = gerar_legenda(image=b"fake", tom="formal", tema="profissional")
        assert "erro" in str(resultado).lower()
