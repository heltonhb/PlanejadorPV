"""
Configurações centralizadas do PlanejadorPV.

Todas as constantes de configuração do sistema vivem aqui.
Altere valores neste arquivo para ajustar comportamento global.
"""

from pathlib import Path

# ── Modelos de IA ──
MODELO_GEMINI = "gemini-2.5-flash"
MODELOS_FALLBACK_GEMINI = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

# ── RAG (Retrieval-Augmented Generation) ──
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_PADRAO = 12
TOP_K_CALENDARIO = 10
TOP_K_CAMPANHA = 8
TOP_K_LEGENDAS = 6

# ── Cache ──
CACHE_SIZE = 256

# ── Rate Limiting (Gemini Free Tier) ──
RATE_LIMIT_INTERVALO = 7

# ── Caminhos ──
CHROMA_PATH = Path("vector_store")
COLLECTION_NAME = "documentos_ensina_mais"
TESSDATA_PATH = Path("tessdata")
TESSDATA_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata"

# ── Retry ──
MAX_RETRIES_GEMINI = 3
BACKOFF_BASE = 2

# ── IA ──
TEMPERATURA_PADRAO = 0.7
MAX_TOKENS_PADRAO = 8192
MAX_TOKENS_LEGENDAS = 4096
MAX_TOKENS_CALENDARIO = 4096
MAX_TOKENS_CAMPANHA = 4096
