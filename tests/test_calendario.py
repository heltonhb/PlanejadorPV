import os
from unittest.mock import MagicMock, patch

import pytest

from utils.calendario import gerar_calendario


class TestGerarCalendario:
    def test_sem_api_key_retorna_erro(self):
        with patch.dict(os.environ, {}, clear=True):
            resultado = gerar_calendario("Janeiro", 2026)
        assert resultado["status"] == "erro"
        assert "não configurada" in resultado["mensagem"]

    def test_mes_invalido_retorna_erro(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with pytest.raises(ValueError):
                gerar_calendario("InvalidMonth", 2026)

    @patch("utils.calendario._get_collection")
    @patch("google.genai.Client")
    def test_sem_contexto_chama_gemini(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "## Janeiro — Visão Geral\n\nConteúdo do calendário."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_calendario("Janeiro", 2026)
        assert resultado["status"] == "ok"
        assert "Conteúdo do calendário" in resultado["conteudo"]
        assert resultado["contexto_usado"] is False

    @patch("utils.calendario._get_collection")
    @patch("google.genai.Client")
    def test_com_contexto_chama_gemini(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_collection.query.return_value = {"documents": [["doc1", "doc2"]]}
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "## Janeiro — Visão Geral\n\nConteúdo personalizado."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_calendario("Janeiro", 2026)
        assert resultado["status"] == "ok"
        assert resultado["contexto_usado"] is True

    @patch("utils.calendario._get_collection")
    @patch("google.genai.Client")
    def test_erro_gemini_retorna_erro(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.models.generate_content.side_effect = Exception("Erro API")

        resultado = gerar_calendario("Janeiro", 2026)
        assert resultado["status"] == "erro"
        assert "Erro ao comunicar" in resultado["mensagem"]

    @patch("utils.calendario._get_collection")
    @patch("google.genai.Client")
    def test_resposta_vazia_retorna_erro(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = ""
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_calendario("Janeiro", 2026)
        assert resultado["status"] == "erro"
        assert "vazia" in resultado["mensagem"]
