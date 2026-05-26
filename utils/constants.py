"""
Constantes de domínio do PlanejadorPV.

Agrupa todas as listas de opções e dicionários usados nas abas
do sistema. Facilita manutenção e evita duplicação entre módulos.
"""

# ── Calendário Editorial ──
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

# ── Campanhas ──
OBJETIVOS = [
    "Atrair novos alunos",
    "Reaquecer leads antigos",
    "Fidelizar alunos atuais",
    "Divulgar novo serviço ou curso",
    "Promover matrículas (ação sazonal)",
    "Gerar indicação de alunos",
]

PUBLICOS = [
    "Fundamental I (6 a 10 anos)",
    "Fundamental II (11 a 15 anos)",
    "Ambos (Fundamental I e II)",
    "Responsáveis dos alunos",
]

SERVICOS = [
    "Apoio escolar — Português",
    "Apoio escolar — Matemática",
    "Tecnologia — Programação",
    "Tecnologia — Robótica",
    "Todos os serviços",
]

# ── Legendas Instagram ──
TOM_ESTILO = {
    "Educativo": "Tom didático e informativo, explicando conceitos ou métodos de ensino.",
    "Promocional": "Tom persuasivo com senso de urgência, focado em matrículas e ofertas.",
    "Inspiracional": "Tom emotivo e motivacional, destacando conquistas e potencial dos alunos.",
    "Engajamento": "Tom de pergunta ou desafio, estimulando interação nos comentários.",
    "Depoimento": "Tom de caso real, contando uma história de sucesso em primeira pessoa.",
}

# ── Dashboard ──
ICONES_FONTE = {
    "pdf": "\U0001f4c4",
    "url": "\U0001f517",
    "html": "\U0001f310",
    "instagram": "\U0001f4f7",
    "texto": "\U0001f4dd",
}

CORES_GRAFICOS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#BB8FCE", "#85C1E9", "#F0B27A", "#82E0AA",
]
