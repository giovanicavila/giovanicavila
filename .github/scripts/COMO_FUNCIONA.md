# 🌠 Como Criar Animação de Meteoros no Gráfico de Contribuições

## Visão Geral

Este guia ensina a criar uma animação customizada SVG que mostra meteoros caindo sobre seu gráfico de contribuições do GitHub.

## Como Funciona

### 1. Buscar Dados do GitHub

Usamos a **API GraphQL** do GitHub para obter suas contribuições:

```python
query = """
query($username: String!) {
    user(login: $username) {
        contributionsCollection {
            contributionCalendar {
                weeks {
                    contributionDays {
                        contributionCount
                        contributionLevel  # NONE, FIRST_QUARTILE, etc.
                        date
                    }
                }
            }
        }
    }
}
"""
```

A resposta traz cada dia do último ano com:
- `contributionCount`: número de commits
- `contributionLevel`: intensidade (0-4) para colorir o quadrado

---

### 2. Gerar o SVG Base (Grid de Contribuições)

SVG é como HTML para gráficos vetoriais. Cada quadradinho é um `<rect>`:

```xml
<rect 
    x="40"          <!-- posição horizontal -->
    y="20"          <!-- posição vertical -->
    width="11"      <!-- largura -->
    height="11"     <!-- altura -->
    fill="#26a641"  <!-- cor baseada no nível -->
    rx="2"          <!-- cantos arredondados -->
/>
```

O grid tem 53 colunas (semanas) × 7 linhas (dias da semana).

---

### 3. Animações SVG Nativas

SVG suporta animações sem JavaScript usando estas tags:

#### `<animate>` - Anima propriedades simples
```xml
<circle r="5">
    <animate
        attributeName="r"       <!-- propriedade a animar -->
        values="5;10;5"         <!-- valores (início;meio;fim) -->
        dur="1s"                <!-- duração -->
        repeatCount="indefinite" <!-- repetir infinito -->
    />
</circle>
```

#### `<animateTransform>` - Move/rotaciona elementos
```xml
<g>
    <animateTransform
        attributeName="transform"
        type="translate"        <!-- tipo: translate, rotate, scale -->
        from="0,0"              <!-- posição inicial -->
        to="100,150"            <!-- posição final -->
        dur="2s"
        begin="0.5s"            <!-- delay para começar -->
        repeatCount="indefinite"
    />
</g>
```

---

### 4. Criando um Meteoro

Um meteoro é composto por:

```xml
<g id="meteor">
    <!-- Rastro (linha com gradiente) -->
    <line x1="0" y1="0" x2="-20" y2="-20"
          stroke="url(#meteor-gradient)"
          stroke-width="4"
          filter="url(#glow)"/>  <!-- filtro de brilho -->
    
    <!-- Núcleo brilhante -->
    <circle cx="0" cy="0" r="3" fill="#ffd700">
        <!-- Pulsar -->
        <animate attributeName="r" values="3;6;3" dur="0.3s" repeatCount="indefinite"/>
    </circle>
    
    <!-- Movimento diagonal -->
    <animateTransform
        attributeName="transform"
        type="translate"
        from="50,-30"           <!-- começa fora da tela -->
        to="150,120"            <!-- termina dentro do grid -->
        dur="2s"
        repeatCount="indefinite"
    />
</g>
```

---

### 5. Filtros e Gradientes (Efeitos Visuais)

Definidos em `<defs>` e referenciados por `url(#id)`:

```xml
<defs>
    <!-- Filtro de glow/brilho -->
    <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
    
    <!-- Gradiente do rastro -->
    <linearGradient id="meteor-gradient">
        <stop offset="0%" style="stop-color:#ffd700"/>    <!-- amarelo -->
        <stop offset="100%" style="stop-color:#ff6b35"/>  <!-- laranja -->
    </linearGradient>
</defs>
```

---

### 6. Explosões de Impacto

Partículas que se espalham do ponto de impacto:

```xml
<circle cx="100" cy="80" r="2" fill="#ff6b35" opacity="0">
    <!-- Move para fora -->
    <animate attributeName="cx" from="100" to="115" dur="0.5s" begin="2s"/>
    <animate attributeName="cy" from="80" to="65" dur="0.5s" begin="2s"/>
    
    <!-- Fade out -->
    <animate attributeName="opacity" values="0;1;0" dur="0.5s" begin="2s"/>
    
    <!-- Encolhe -->
    <animate attributeName="r" from="3" to="0" dur="0.5s" begin="2s"/>
</circle>
```

---

## Propriedades Animáveis Úteis

| Propriedade | Tipo | Exemplo |
|-------------|------|---------|
| `opacity` | 0-1 | Fade in/out |
| `fill` | cor | Mudar cor |
| `r` | número | Tamanho de círculo |
| `cx`, `cy` | número | Posição de círculo |
| `x`, `y` | número | Posição de rect |
| `transform` | translate/rotate/scale | Mover/girar/escalar |
| `stroke-dashoffset` | número | Animação de linha "desenhando" |

---

## Estrutura do Projeto

```
.github/
├── scripts/
│   ├── generate_meteor_animation.py  # Script que gera o SVG
│   └── COMO_FUNCIONA.md              # Esta documentação
└── workflows/
    └── meteor.yml                     # GitHub Action que executa
```

---

## Personalizações Possíveis

1. **Mudar cores**: Edite o dicionário `COLORS`
2. **Mais/menos meteoros**: Altere `num_meteors`
3. **Velocidade**: Ajuste `duration` nos meteoros
4. **Tamanho dos quadrados**: Mude `CELL_SIZE` e `CELL_GAP`

---

## Ideias para Outras Animações

- **Pacman**: Um círculo com "boca" que se move pelo grid
- **Foguete**: `<polygon>` com rastro de fogo
- **Partículas**: Commits que explodem e se espalham
- **Onda**: Efeito de onda passando pelo grid (animando `y` de cada coluna com delay)
- **Matrix**: Caracteres caindo estilo Matrix

---

## Referências

- [SVG Animation MDN](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [SVG Filters](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/filter)
