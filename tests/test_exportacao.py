import csv
import io

from utils.exportacao import exportar_markdown_docx, exportar_relatorio_csv


class TestExportarRelatorioCsv:
    def test_retorna_string_csv_valida(self):
        relatorio = {
            "fontes_detalhadas": [
                {"fonte": "pdf", "titulo": "doc1", "chunks": 3, "caracteres": 100, "resumo": "Resumo A"},
                {"fonte": "url", "titulo": "doc2", "chunks": 5, "caracteres": 200, "resumo": "Resumo B"},
            ]
        }
        resultado = exportar_relatorio_csv(relatorio)
        assert isinstance(resultado, str)
        linhas = resultado.strip().split("\n")
        assert len(linhas) == 3

    def test_csv_pode_ser_lido_por_csv_reader(self):
        relatorio = {
            "fontes_detalhadas": [
                {"fonte": "pdf", "titulo": "Doc A", "chunks": 1, "caracteres": 100, "resumo": "Resumo A"}
            ]
        }
        csv_str = exportar_relatorio_csv(relatorio)
        reader = csv.DictReader(io.StringIO(csv_str))
        linhas = list(reader)
        assert len(linhas) == 1
        assert linhas[0]["Título"] == "Doc A"

    def test_relatorio_vazio_retorna_apenas_cabecalho(self):
        relatorio = {"fontes_detalhadas": []}
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
