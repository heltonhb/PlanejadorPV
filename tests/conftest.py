import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def env_setup():
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    from utils.gemini_client import reset_cliente
    reset_cliente()


@pytest.fixture
def mock_gemini():
    with patch("google.genai.Client") as mock_client_class:
        instance = MagicMock()
        mock_client_class.return_value = instance
        response = MagicMock()
        response.text = "Resposta simulada do Gemini."
        instance.models.generate_content.return_value = response
        yield mock_client_class
