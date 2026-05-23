"""
Modelos Pydantic para o sistema RAG (Retrieval-Augmented Generation).
"""

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    """
    Requisição para consulta ao sistema RAG.
    
    Attributes:
        pergunta: A pergunta do usuário.
        top_k: Número de chunks a recuperar (entre 1 e 20).
    """
    pergunta: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Pergunta do usuário para consulta",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Número de chunks a recuperar (1-20)",
    )

    model_config = {"populate_by_name": True}

    @field_validator("pergunta")
    @classmethod
    def pergunta_nao_pode_ser_vazia(cls, v: str) -> str:
        """Valida que a pergunta não é apenas espaços em branco."""
        if not v or not v.strip():
            raise ValueError("Pergunta não pode ser vazia")
        return v.strip()


class ChunkRecuperado(BaseModel):
    """
    Representa um chunk de documento recuperado do vector store.
    """
    texto: str = Field(
        ...,
        description="Conteúdo textual do chunk",
    )
    chunk_id: str = Field(
        ...,
        description="Identificador único do chunk",
    )
    fonte: str = Field(
        default="desconhecida",
        description="Fonte/origem do chunk",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Metadados adicionais do chunk",
    )

    model_config = {"populate_by_name": True}


class QueryResponse(BaseModel):
    """
    Resposta de uma consulta ao sistema RAG.
    """
    pergunta: str = Field(
        ...,
        description="Pergunta original do usuário",
    )
    resposta: str = Field(
        ...,
        description="Resposta gerada pelo modelo",
    )
    contexto: str = Field(
        ...,
        description="Contexto combinado dos chunks recuperados",
    )
    chunks_recuperados: list[ChunkRecuperado] = Field(
        default_factory=list,
        description="Lista de chunks usados para gerar a resposta",
    )

    model_config = {"populate_by_name": True}

    @field_validator("resposta", "contexto")
    @classmethod
    def campos_nao_devem_ser_nulos(cls, v: str) -> str:
        """Valida que campos de texto não são None."""
        return v or ""
