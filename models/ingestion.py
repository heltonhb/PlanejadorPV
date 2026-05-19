from typing import Literal, Union

from pydantic import BaseModel, Field


class IngestionError(BaseModel):
    status: Literal["erro"] = "erro"
    mensagem: str

    model_config = {"populate_by_name": True}


class PDFResult(BaseModel):
    status: Literal["ok"] = "ok"
    total_chunks: int = Field(ge=0)
    total_caracteres: int = Field(ge=0)
    paginas: int = Field(ge=0)
    metodo: str

    model_config = {"populate_by_name": True}


class URLResult(BaseModel):
    status: Literal["ok"] = "ok"
    total_chunks: int = Field(ge=0)
    total_caracteres: int = Field(ge=0)
    titulo: str
    url: str

    model_config = {"populate_by_name": True}


class HTMLResult(BaseModel):
    status: Literal["ok"] = "ok"
    total_chunks: int = Field(ge=0)
    total_caracteres: int = Field(ge=0)
    titulo: str
    arquivo: str

    model_config = {"populate_by_name": True}


class InstagramResult(BaseModel):
    status: Literal["ok"] = "ok"
    total_chunks: int = Field(ge=0)
    total_caracteres: int = Field(ge=0)
    perfil: str
    posts: int = Field(ge=0)

    model_config = {"populate_by_name": True}


IngestionResult = Union[PDFResult, URLResult, HTMLResult, InstagramResult, IngestionError]
