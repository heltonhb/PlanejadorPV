import os
from unittest.mock import MagicMock, patch

from utils.resumos import gerar_resumo


class TestGerarResumo:
    def test_texto_vazio_retorna_erro(self):
        resultado = gerar_resumo("", fonte="documento")
        assert "erro" in resultado.lower()

    def test_sem_api_key_retorna_mensagem_erro(self):
        with patch.dict(os.environ, {}, clear=True):
            resultado = gerar_resumo("Texto qualquer para resumo.", fonte="documento")
        assert "erro" in str(resultado).lower()

    @patch("google.genai.Client")
    def test_retorna_resumo_do_gemini(self, mock_client_class):
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "Resumo gerado pelo Gemini."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_resumo("Texto longo para ser resumido.", fonte="documento")
        assert resultado == "Resumo gerado pelo Gemini."

    @patch("google.genai.Client")
    def test_erro_gemini_retorna_mensagem_erro(self, mock_client_class):
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.models.generate_content.side_effect = Exception("Erro API")

        resultado = gerar_resumo("Texto que causa erro.", fonte="documento")
        assert "erro" in resultado.lower()
