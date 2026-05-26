import os
from unittest.mock import MagicMock, patch

from utils.campanhas import gerar_campanha


class TestGerarCampanha:
    @patch("utils.gemini_client._get_gemini_key", return_value=None)
    def test_sem_api_key_retorna_erro(self, mock_get_key):
        with patch.dict(os.environ, {}, clear=True):
            resultado = gerar_campanha(
                objetivo="Atrair novos alunos",
                publico="Fundamental I (6 a 10 anos)",
                servico="Apoio escolar — Português",
            )
        assert resultado["status"] == "erro"
        assert "não configurada" in resultado["mensagem"]

    @patch("utils.campanhas._get_collection")
    @patch("google.genai.Client")
    def test_sem_contexto_chama_gemini(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "## Campanha de Marketing\n\nConteúdo da campanha."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_campanha(
            objetivo="Atrair novos alunos",
            publico="Fundamental I (6 a 10 anos)",
            servico="Apoio escolar — Português",
        )
        assert resultado["status"] == "ok"
        assert "Conteúdo da campanha" in resultado["conteudo"]
        assert resultado["contexto_usado"] is False

    @patch("utils.campanhas._get_collection")
    @patch("google.genai.Client")
    def test_com_contexto_chama_gemini(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 3
        mock_collection.query.return_value = {"documents": [["ctx1"]]}
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "## Campanha Personalizada\n\nConteúdo com contexto."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_campanha(
            objetivo="Fidelizar alunos atuais",
            publico="Ambos (Fundamental I e II)",
            servico="Todos os serviços",
        )
        assert resultado["status"] == "ok"
        assert resultado["contexto_usado"] is True

    @patch("utils.campanhas._get_collection")
    @patch("google.genai.Client")
    def test_com_todos_parametros_opcionais(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = "## Campanha Completa\n\nConteúdo com todos os parâmetros."
        mock_instance.models.generate_content.return_value = mock_response

        resultado = gerar_campanha(
            objetivo="Divulgar novo serviço ou curso",
            publico="Fundamental II (11 a 15 anos)",
            servico="Tecnologia — Programação",
            nome="Semana da Programação",
            canais=["Instagram", "WhatsApp"],
            orcamento=500.0,
            datas="01/03/2026 a 15/03/2026",
        )
        assert resultado["status"] == "ok"
        assert resultado["contexto_usado"] is False

    @patch("utils.campanhas._get_collection")
    @patch("google.genai.Client")
    def test_erro_gemini_retorna_erro(self, mock_client_class, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.models.generate_content.side_effect = Exception("Erro API")

        resultado = gerar_campanha(
            objetivo="Atrair novos alunos",
            publico="Fundamental I (6 a 10 anos)",
            servico="Apoio escolar — Português",
        )
        assert resultado["status"] == "erro"
        assert "inesperado" in resultado["mensagem"]

    @patch("utils.campanhas._get_collection")
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

        resultado = gerar_campanha(
            objetivo="Atrair novos alunos",
            publico="Fundamental I (6 a 10 anos)",
            servico="Apoio escolar — Português",
        )
        assert resultado["status"] == "erro"
        assert "vazia" in resultado["mensagem"]
