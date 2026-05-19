from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    pergunta: str
    top_k: int = Field(default=5, ge=1, le=20)

    model_config = {"populate_by_name": True}


class ChunkRecuperado(BaseModel):
    texto: str
    chunk_id: str
    fonte: str
    metadata: dict = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class QueryResponse(BaseModel):
    pergunta: str
    resposta: str
    contexto: str
    chunks_recuperados: list[ChunkRecuperado] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
