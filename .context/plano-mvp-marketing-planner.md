# Plano Detalhado — MVP Marketing Planner Ensina Mais

## Visão Geral
App web de baixo custo que usa Google Gemini API para criar um "cérebro" com seus documentos da franquia e gerar planos de marketing personalizados para sua unidade do Tatuapé.

**Custo mensal:** R$ 0 (apenas o tempo de desenvolvimento)  
**Tecnologia:** Streamlit (Python) + Google Gemini API  
**Prazo:** 14 dias  

---

## 📁 Estrutura do Projeto

```
marketing-planner/
├── app.py                 # App principal (Streamlit)
├── requirements.txt       # Dependências
├── .env                   # Chave da API Gemini
├── documentos/            # Seus PDFs (manual, planilhas, etc.)
│   └── (seus arquivos)
├── vector_store/          # Memória da IA (criado automaticamente)
│   └── index.faiss
└── utils/
    ├── documentos.py      # Funções de upload e extração de PDF
    ├── ia_engine.py       # Motor RAG (Gemini + busca em documentos)
    ├── calendario.py      # Geração de calendário de marketing
    └── campanhas.py       # Gerador de campanhas
```

---

## 🧱 Módulo 1 — Setup do Projeto (Dia 1)

### O que instalar

```bash
pip install streamlit google-generativeai python-dotenv
pip install PyPDF2 pdfplumber langchain-community
pip install faiss-cpu chromadb sentence-transformers
```

### Arquivo `.env`

```
GEMINI_API_KEY=sua_chave_aqui
```

> **Como obter a chave:** Acesse [aistudio.google.com](https://aistudio.google.com/) → Get API Key → Criar chave → Grátis!

### `requirements.txt`

```
streamlit==1.35.0
google-generativeai==0.7.2
python-dotenv==1.0.1
PyPDF2==3.0.1
pdfplumber==0.11.0
faiss-cpu==1.8.0
chromadb==0.5.0
langchain-community==0.2.0
```

---

## 🧱 Módulo 2 — Upload de Documentos (Dias 2-3)

### Arquivo: `utils/documentos.py`

**O que faz:**
1. Recebe PDFs enviados pelo usuário
2. Extrai texto usando `pdfplumber`
3. Divide em "pedaços" (chunks) de ~500 caracteres
4. Salva o texto extraído para o motor de IA usar

### Fluxo:

```
Usuário faz upload do PDF
        │
        ▼
Extrair texto do PDF
        │
        ▼
Dividir em chunks (com sobreposição)
        │
        ▼
Salvar chunks no vetor store (memória da IA)
        │
        ▼
"Manual da franquia carregado! ✅"
```

### Tela no app:

```python
# app.py
uploaded_file = st.file_uploader("📄 Carregue seus documentos", type="pdf")
if uploaded_file:
    with st.spinner("Processando documento..."):
        processar_documento(uploaded_file)
    st.success("Documento processado! IA aprendeu com ele ✅")
```

---

## 🧱 Módulo 3 — Motor de IA (RAG) — O Coração do App (Dias 4-6)

### Arquivo: `utils/ia_engine.py`

Este é o módulo que **reproduz a inteligência do NotebookLM** dentro do app.

### Como funciona o RAG (Retrieval Augmented Generation):

```
PERGUNTA DO USUÁRIO
"O que fazer em maio para robótica?"
        │
        ▼
  1. CONVERTE pergunta em vetor (embedding)
        │
        ▼
  2. BUSCA nos documentos os chunks mais parecidos
        │
        ▼
  3. ENVIA para o Gemini:
     "Responda com base APENAS nestes trechos:
      [trecho 1], [trecho 2]...
      Pergunta: O que fazer em maio para robótica?"
        │
        ▼
  4. GEMINI RESPONDE com base SOMENTE nos seus documentos
        │
        ▼
  RESPOSTA: "Com base no manual da franquia..."
```

### Código principal:

```python
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions

# Configurar Gemini
genai.configure(api_key="...")
model = genai.GenerativeModel('gemini-1.5-flash')

# Criar banco de vetores (memória dos documentos)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name="documentos_ensina_mais"
)

def perguntar(pergunta):
    """Faz uma pergunta com base nos documentos carregados"""
    
    # 1. Busca trechos relevantes nos documentos
    resultados = collection.query(
        query_texts=[pergunta],
        n_results=5
    )
    
    # 2. Monta contexto com os trechos encontrados
    contexto = "\n\n".join(resultados['documents'][0])
    
    # 3. Envia para o Gemini
    prompt = f"""Você é um consultor de marketing especializado em 
    franquias educacionais. Responda à pergunta usando APENAS as 
    informações fornecidas abaixo. Se não encontrar a resposta, 
    diga que não há informação suficiente.
    
    Documentos de referência:
    {contexto}
    
    Pergunta: {pergunta}
    """
    
    resposta = model.generate_content(prompt)
    return resposta.text
```

### Modelo de IA usado:

| Modelo | Vantagem | Custo |
|---|---|---|
| **Gemini 1.5 Flash** 🏆 | Rápido, contexto de 1M tokens, grátis até 1500 requisições/dia | Grátis |
| Gemini 1.5 Pro | Mais potente, contexto maior | US$ ~3-7/mês |

> 💡 **Recomendação**: Comece com **Gemini 1.5 Flash** — é rápido, inteligente e gratuito.

---

## 🧱 Módulo 4 — Assistente de Marketing (Dias 7-8)

### Interface no `app.py`

```python
st.title("💬 Assistente de Marketing")

# Histórico da conversa
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Mostrar conversa
for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).write(msg["content"])

# Input do usuário
pergunta = st.chat_input("Faça uma pergunta sobre marketing...")
if pergunta:
    # Mostra pergunta do usuário
    st.chat_message("user").write(pergunta)
    
    # Gera resposta com IA
    with st.spinner("Consultando seus documentos..."):
        resposta = perguntar(pergunta)
    
    # Mostra resposta
    st.chat_message("assistant").write(resposta)
    
    # Salva no histórico
    st.session_state.mensagens.append(
        {"role": "user", "content": pergunta}
    )
    st.session_state.mensagens.append(
        {"role": "assistant", "content": resposta}
    )
```

### Sugestões de perguntas que o assistente responde:

| Pergunta | Como a IA responde |
|---|---|
| "Como atrair mais alunos para programação?" | Baseado no manual da franquia + dados de concorrência |
| "Qual melhor época para campanha de matrículas?" | Baseado em dados sazonais dos seus documentos |
| "Que conteúdo postar no Instagram esta semana?" | Baseado nas personas dos alunos/responsáveis |
| "Como divulgar robótica para Fund I?" | Baseado nas diretrizes da franquia |

---

## 🧱 Módulo 5 — Calendário Inteligente (Dias 9-10)

### Arquivo: `utils/calendario.py`

O calendário é **gerado pela IA** com base nos seus documentos. A IA sabe:
- Épocas de matrícula (início e meio do ano)
- Períodos de provas (maio, outubro)
- Férias escolares (julho, dezembro/janeiro)
- Eventos da franquia

### Como gera:

```python
def gerar_calendario(mes, documentos):
    prompt = f"""
    Com base nos documentos da franquia Ensina Mais Turma da Mônica,
    crie um plano de ações de marketing para {mes}.
    
    Considere:
    - Público: Fundamental I e II
    - Serviços: apoio escolar (português/matemática) e 
      tecnologia (programação/robótica)
    - Unidade: Tatuapé - SP
    - Concorrência local (dos documentos)
    
    Para cada semana, sugira 2-3 ações específicas.
    """
    
    return model.generate_content(prompt).text
```

### Exemplo de saída:

```
📅 JULHO - FÉRIAS!

Semana 1 (01-07 jul):
  🎯 Campanha "Férias Tecnológicas" — Programação e Robótica
  📱 Post Instagram: Carrossel "5 motivos para seu filho aprender 
     programação nas férias"
  📞 WhatsApp: Oferta especial de julho para matrículas em tecnologia

Semana 2 (08-14 jul):
  🎯 Ação "Revisão de Volta às Aulas" — Português e Matemática
  📱 Post Instagram: Depoimento de aluno
  📞 WhatsApp: Dica de estudo para o 2º semestre

... e assim para o mês todo
```

---

## 🧱 Módulo 6 — Gerador de Campanhas (Dias 11-12)

### Arquivo: `utils/campanhas.py`

Gera uma campanha de marketing completa com:

```python
def gerar_campanha(objetivo, publico, servico):
    """
    objetivo: "atrair novos alunos", "reaquecer leads", etc.
    publico: "Fundamental I", "Fundamental II", "ambos"
    servico: "programação", "robótica", "português", "matemática"
    """
    
    prompt = f"""
    Crie uma campanha de marketing completa para:
    
    Franquia: Ensina Mais Turma da Mônica
    Unidade: Tatuapé - SP
    Objetivo: {objetivo}
    Público-alvo: {publico}
    Serviço: {servico}
    
    Use as informações dos documentos para personalizar.
    
    Formato da resposta:
    
    🎯 NOME DA CAMPANHA:
    [nome criativo]
    
    📋 DESCRIÇÃO:
    [descrição da campanha]
    
    📱 CANAIS:
    - Instagram: [ideias de posts/reels]
    - WhatsApp: [texto para disparo]
    - Material impresso: [ideia de flyer/cartaz]
    
    📅 CRONOGRAMA:
    - Semana 1: [ação]
    - Semana 2: [ação]
    - Semana 3: [ação]
    
    💰 INVESTIMENTO SUGERIDO:
    [estimativa com base em ações similares]
    """
    
    return model.generate_content(prompt).text
```

---

## 🧱 Módulo 7 — Deploy (Dia 13)

### Subir na Streamlit Community Cloud (Grátis)

1. Crie um repositório no GitHub com seu código
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu GitHub e selecione o repositório
4. Configure a chave da API Gemini como **Secrets**:

```toml
# Secrets do Streamlit Cloud
GEMINI_API_KEY = "sua_chave_aqui"
```

5. Pronto! Seu app estará online em:  
   `https://seuapp.streamlit.app`

### Alternativas gratuitas:

| Plataforma | Limite | Ideal para |
|---|---|---|
| **Streamlit Cloud** 🏆 | 1 app público, 1GB RAM | MVP perfeito |
| **Hugging Face Spaces** | Grátis, CPU básico | Testes |
| **Google Colab** | Sessões temporárias | Prototipagem |

---

## 🧪 Plano de Testes (Dia 14)

### Teste com seus documentos reais

| Teste | O que verificar |
|---|---|
| 1. Upload do Manual da Franquia | Extraiu texto corretamente? |
| 2. Pergunta: "Qual nossa proposta de valor?" | A resposta está alinhada com o manual? |
| 3. Pergunta: "O que fazer em fevereiro?" | Sugeriu campanha de volta às aulas? |
| 4. Gerar campanha de robótica | Usou dados da concorrência do Tatuapé? |
| 5. Testar em celular | O layout responsivo funciona? |

---

## 📈 Pós-MVP — Próximos Passos

### Se o MVP funcionar bem:

```
Fase 1 (MVP) ───> Fase 2 (App Completo) ───> Fase 3 (Avançado)
   Streamlit           Next.js + React         App Mobile
   R$ 0/mês            R$ 50-80/mês            R$ 100-150/mês
   Grátis              Dados persistentes       IA + Automação
                       Mais funcionalidades     Integração APIs
```

### O que vem depois:

| Fase | Funcionalidades novas | Investimento |
|---|---|---|
| **Fase 2** | Banco PostgreSQL, calendário editável, dashboard de resultados, login de usuário, exportar PDF | ~R$ 3.000-5.000 |
| **Fase 3** | Integração Instagram (api), envio automático WhatsApp, app mobile (React Native), relatórios automáticos | ~R$ 8.000-15.000 |

---

## ✅ Checklist Final

- [ ] Chave da API Gemini criada (grátis)
- [ ] Ambiente Python configurado
- [ ] Upload de documentos funcionando
- [ ] Motor RAG respondendo com base nos docs
- [ ] Chat assistente operacional
- [ ] Calendário gerando sugestões
- [ ] Gerador de campanhas pronto
- [ ] App no ar (Streamlit Cloud)
- [ ] Testado com documentos reais

---

**Pronto para começar?** Com este plano, em 14 dias você terá um app funcional que usa IA para planejar o marketing da sua unidade — tudo por **R$ 0/mês**.
