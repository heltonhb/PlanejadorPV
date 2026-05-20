import csv
import io
import re


def exportar_relatorio_csv(relatorio: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fonte", "Título", "Chunks", "Caracteres", "Resumo"])
    for item in relatorio.get("fontes_detalhadas", []):
        writer.writerow([
            item.get("fonte", ""),
            item.get("titulo", ""),
            item.get("chunks", 0),
            item.get("caracteres", 0),
            item.get("resumo", ""),
        ])
    return output.getvalue()


def exportar_markdown_docx(conteudo_md: str) -> bytes:
    from docx import Document

    doc = Document()
    for line in conteudo_md.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            _add_rich_text(p, line[2:])
        elif line[0].isdigit() and ". " in line[:4]:
            p = doc.add_paragraph(style="List Number")
            _add_rich_text(p, line.split(". ", 1)[1])
        else:
            p = doc.add_paragraph()
            _add_rich_text(p, line)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def _add_rich_text(paragraph, text: str):
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)
