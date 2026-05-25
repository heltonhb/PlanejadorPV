# Design System: Marketing Planner (PlanejadorPV)

**Projeto:** App Streamlit para gestão de marketing da franquia educacional Ensina Mais Turma da Mônica

## 1. Visual Theme & Atmosphere

**Escuro (padrão):** Uma estética dark-mode refinada com inspiração em dashboards modernos. O fundo é um preto-azulado profundo (`#0D1117`, similar ao GitHub Dark), criando uma tela que destaca os elementos coloridos. A atmosfera é **profissional, tecnológica e focada** — como um cockpit de analytics. As superfícies de cartão têm um tom ligeiramente mais claro (`#161B22`) que se eleva sobre o fundo, criando uma hierarquia visual sutil.

**Claro:** Uma variação limpa e arejada com fundo off-white (`#F8F9FA`) e superfícies brancas puras (`#FFFFFF`). Os verdes do branding tornam-se mais escuros e corporativos (`#006D38`), transmitindo seriedade e confiança. A transição entre temas é fluida, mantendo a mesma arquitetura visual.

**Gradiente do cabeçalho:** Um gradiente linear verde (`#006D38` → `#00A859`) atravessa o topo, ancorando a identidade visual com um elemento marcante e energético.

## 2. Color Palette & Roles

### Tema Escuro (Padrão)

| Cor | Hex | Função |
|---|---|---|
| **Verde Vibrante (Primária)** | `#00A859` | Ações principais, botões primários, indicadores ativos |
| **Verde Escuro (Primary Dark)** | `#007A40` | Hover de botões primários |
| **Verde Claro** | `#4ADE80` | Texto em container primário, destaque sidebar |
| **Container Primário** | `rgba(0, 168, 89, 0.12)` | Fundo de mensagens do usuário, badges ativos |
| **Azul Informação** | `#3B82F6` | Ações secundárias, links informativos |
| **Azul Escuro (Info Dark)** | `#2563EB` | Hover de botões secundários |
| **Amarelo Alerta** | `#F7B731` | Alertas, badgets de atenção |
| **Vermelho Erro** | `#EF4444` | Erros, ações destrutivas |
| **Fundo Principal** | `#0D1117` | Background da página |
| **Superfície Cartão** | `#161B22` | Cards, containers, expanders |
| **Texto Principal** | `#E6EDF3` | Títulos e corpo |
| **Texto Variante** | `#A0ABB3` | Labels, captions, metadados |
| **Borda** | `#30363D` | Bordas de containers, separadores |
| **Borda Variante** | `#21262D` | Bordas internas sutis |

### Tema Claro

| Cor | Hex | Função |
|---|---|---|
| **Verde Corporativo (Primária)** | `#006D38` | Ações principais, botões primários |
| **Primary Dark** | `#005A2E` | Hover de botões primários |
| **Container Primário** | `#E8F5E9` | Fundo de mensagens do usuário |
| **Azul Informação** | `#005CAA` | Ações secundárias |
| **Fundo Principal** | `#F8F9FA` | Background da página |
| **Superfície Cartão** | `#FFFFFF` | Cards, containers |
| **Texto Principal** | `#1A1C1E` | Títulos e corpo |
| **Texto Variante** | `#44474E` | Labels, captions |
| **Borda** | `#74777F` | Bordas de containers |
| **Borda Variante** | `#C4C6D0` | Bordas internas sutis |

### Elementos Compartilhados

| Elemento | Valor |
|---|---|
| **Sombra leve** | `0 2px 4px rgba(0,0,0,0.3)` (escuro) / `0 2px 4px rgba(0,0,0,0.05)` (claro) |
| **Sombra média** | `0 4px 12px rgba(0,0,0,0.4)` (escuro) / `0 4px 12px rgba(0,0,0,0.08)` (claro) |
| **Sombra intensa** | `0 12px 24px rgba(0,0,0,0.5)` (escuro) / `0 12px 24px rgba(0,0,0,0.12)` (claro) |
| **Glassmorphism** | Fundo semi-transparente + `blur(12px)` + borda sutil |

## 3. Typography Rules

- **Família principal:** `Inter` (Google Fonts), com fallback para `system-ui, -apple-system, sans-serif`
- **Cabeçalhos:** Peso 800 (ExtraBold), letter-spacing: -0.5px
- **Subtítulos e labels:** Peso 600 (Semibold)
- **Corpo:** Peso 400 (Regular)
- **Botões:** Peso 700 (Bold), text-transform: uppercase, letter-spacing: 0.5px
- **Sidebar headers:** Peso 700, tamanho 0.75rem, uppercase, letter-spacing: 1.5px
- **Título do app no header:** 1.8rem (1.1rem em mobile)
- **Valores de métricas:** 2.5rem (2rem em mobile), peso 800

## 4. Component Stylings

### Botões

**Primário:**
- Fundo: `var(--primary)` (`#00A859` escuro / `#006D38` claro)
- Forma: cantos sutilmente arredondados (`border-radius: 12px`)
- Sombra: glow verde (`0 4px 14px rgba(0, 168, 89, 0.3)`)
- Hover: fundo escurece (`var(--primary-dark)`), eleva 2px, sombra intensifica
- Texto: branco, uppercase, peso 700

**Secundário/Outline:**
- Borda: `var(--info)` com cantos arredondados
- Fundo: transparente
- Texto: `var(--info)`
- Hover: fundo azul muito sutil, borda escurece

### Cartões de Métrica (Metric Cards)

- Forma: cantos generosamente arredondados (`border-radius: 16px`)
- Fundo: `var(--card-bg)`
- Borda: `var(--outline-variant)` com 1px
- Sombra: leve, com sombra intensificada ao hover
- Hover: eleva 4px, borda assume cor primária (`var(--primary)`)
- Destaque: faixa colorida na borda superior (4px) — verde (métrica positiva), azul (neutra), amarelo (alerta), vermelho (crítica)

### Cartões de Conteúdo (App Cards)

- Forma: cantos generosamente arredondados (`border-radius: 16px`)
- Fundo: `var(--card-bg)`
- Borda: `var(--outline-variant)` com 1px
- Sombra: leve, intensifica ao hover
- Padding interno: 1.75rem

### Inputs e Formulários

- Forma: cantos sutilmente arredondados (`border-radius: 12px`)
- Fundo: `var(--input-bg)` (`#0D1117` escuro / `#FFFFFF` claro)
- Borda: utiliza o padrão Streamlit com cor do outline

### Abas (Tabs)

- Container de abas: fundo levemente escurecido com `border-radius: 12px`
- Abas inativas: texto na cor `var(--on-surface-variant)`, peso 600
- Aba ativa: fundo `var(--surface)` com sombra sutil, texto na cor primária
- Transição suave entre estados

### Chat

**Mensagem do usuário:**
- Fundo: `var(--primary-container)` — verde translúcido
- Borda: verde sutil (`rgba(0, 168, 89, 0.1)`)
- Cantos: sutilmente arredondados (12px)

**Mensagem do assistente:**
- Fundo: `var(--card-bg)`
- Borda: `var(--outline-variant)`
- Sombra: leve
- Cantos: sutilmente arredondados (12px)

### Sidebar

- Fundo: `#0D1117` (mantém escuro mesmo no tema claro — efeito "painel de controle")
- Texto: `rgba(255, 255, 255, 0.7)` com variante ativa em verde claro (`#4ADE80`)
- Radio buttons: item ativo ganha fundo primary-container + borda verde + peso 600
- Headers: uppercase, tracking expandido, opacidade reduzida

### Expanders

- Forma: cantos sutilmente arredondados (`border-radius: 12px`)
- Borda: `var(--outline-variant)`
- Fundo: `var(--card-bg)`

### Tabelas

- Cantos: sutilmente arredondados (12px, com overflow hidden)
- Cabeçalho: fundo levemente destacado, peso 700, border-bottom 2px
- Linhas: border-bottom 1px sutil
- Espaçamento: células com padding 0.85-1rem

## 5. Layout Principles

### Estrutura Geral

- **Sidebar fixa à esquerda** (240px): navegação por tipo de fonte + lista de fontes carregadas
- **Área principal central** (max-width: 1240px): tabs para dashboard, chat, calendário, campanhas, relatórios, legendas
- **Header gradiente** no topo da área principal com logo + saudação + alternador de tema

### Estratégia de Whitespace

- **Padding generoso:** 1.5rem nas laterais, 2rem no header, 1.75rem nos cards
- **Espaçamento entre seções:** 2rem de margin-bottom após o header
- **Espaçamento entre cards:** 1.5rem
- **Mobile:** padding reduz para 1rem, header empilha verticalmente

### Hierarquia Visual

1. **Header gradiente verde** ancora a identidade visual
2. **Tabs de navegação** organizam as seções principais
3. **Cards de métrica** com destaque colorido na borda superior fornecem visão geral
4. **Cartões de conteúdo** agrupam informações relacionadas
5. **Chat** segue padrão de mensagens com bolhas estilizadas

### Responsividade

- Breakpoint: 640px
- Header empilha verticalmente (logo centralizada, saudação e tema abaixo)
- Logo reduz de 80px para 48px
- Bolha decorativa do header oculta
- Tabs permitem scroll horizontal
- Padding geral reduzido

### Elevação e Profundidade

- **Camada base:** Background (`var(--background)`) — nivel 0
- **Camada superfície:** Cards e containers (`var(--card-bg)`) — sombra leve (sm)
- **Camada elevada:** Header e cartões em hover — sombra média (md)
- **Camada flutuante:** Modal, glassmorphism — sombra intensa (lg)
- **Efeito glass:** Elementos com backdrop-filter blur + fundo semi-transparente (header greeting, theme button)

### Animações

- **Fade-in:** Elementos surgem com opacidade 0→1 e translateY(10px)→0 em 0.4s
- **Hover em botões:** Scale(1.05) + transição suave
- **Hover em cards:** TranslateY(-4px) + sombra intensifica
- **Pulse:** Indicador de status com animação pulse infinita (círculo verde)

## 6. Tema Claro vs Escuro

| Aspecto | Escuro | Claro |
|---|---|---|
| Background | Preto-azulado profundo | Off-white suave |
| Superfície | Cinza-escuro | Branco puro |
| Texto | Branco gelo | Preto suave |
| Texto variante | Cinza médio | Cinza escuro |
| Bordas | Cinza escuro | Cinza claro |
| Sidebar | Mantém escuro | Mantém escuro (consistência) |
| Primary | Verde vibrante | Verde corporativo escuro |
| Sombra | Opaca e dramática | Leve e difusa |
