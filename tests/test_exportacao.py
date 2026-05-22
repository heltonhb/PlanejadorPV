import csv
import io

from utils.exportacao import exportar_markdown_docx, exportar_relatorio_csv


class TestExportarRelatorioCsv:
    def test_retorna_string_csv_valida(self):
        relatorio = {
            "documentos": [
                {"id": "doc1", "data": "2025-01-01", "chunks": 3},
                {"id": "doc2", "data": "2025-01-15", "chunks": 5},
            ]
        }
        resultado = exportar_relatorio_csv(relatorio)
        assert isinstance(resultado, str)
        linhas = resultado.strip().split("\n")
        assert len(linhas) == 3

    def test_csv_pode_ser_lido_por_csv_reader(self):
        relatorio = {"documentos": [{"nome": "Doc A", "tamanho": 100}]}
        csv_str = exportar_relatorio_csv(relatorio)
        reader = csv.DictReader(io.StringIO(csv_str))
        linhas = list(reader)
        assert len(linhas) == 1
        assert linhas[0]["nome"] == "Doc A"

    def test_relatorio_vazio_retorna_apenas_cabecalho(self):
        relatorio = {"documentos": []}
        resultado = exportar_relatorio_csv(relatorio)
        linhas = resultado.strip().split("\n")
        assert len(linhas) == 1


class TestExportarMarkdownDocx:
    def test_retorna_bytes(self):
        conteudo_md = "# Título\n\nParágrafo de exemplo."
        resultado = exportar_markdown_docx(conteudo_md)
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_conteudo_vazio_retorna_bytes(self):
        resultado = exportar_markdown_docx("")
        assert isinstance(resultado, bytes)
