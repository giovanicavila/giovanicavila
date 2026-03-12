"""
🌠 GERADOR DE ANIMAÇÃO: CHUVA DE METEOROS NO GRÁFICO DE CONTRIBUIÇÕES
---------------------------------------------------------------------
Este script:
1. Busca suas contribuições do GitHub via GraphQL API
2. Gera um SVG do gráfico de contribuições 
3. Adiciona animações de meteoros caindo e "destruindo" os commits

COMO FUNCIONA O SVG ANIMADO:
- SVG suporta tags <animate> e <animateTransform> nativas
- Podemos animar: posição, opacidade, cor, tamanho, rotação
- As animações rodam no browser sem JavaScript!
"""

import requests
import random
import math
from datetime import datetime, timedelta
import os

# ============================================================
# CONFIGURAÇÕES - Personalize aqui!
# ============================================================
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "giovanicavila")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Cores do gráfico (estilo GitHub Dark)
COLORS = {
    0: "#161b22",  # Sem contribuição
    1: "#0e4429",  # Pouco
    2: "#006d32",  # Médio
    3: "#26a641",  # Bom
    4: "#39d353",  # Muito
}

# Configurações visuais
CELL_SIZE = 11        # Tamanho de cada quadrado
CELL_GAP = 3          # Espaço entre quadrados
WEEKS_TO_SHOW = 53    # Semanas no gráfico (1 ano)


# ============================================================
# PARTE 1: BUSCAR DADOS DO GITHUB
# ============================================================
def fetch_contributions(username: str, token: str) -> list:
    """
    Busca contribuições usando a API GraphQL do GitHub.
    
    A query retorna os últimos 12 meses de contribuições,
    com a contagem de commits por dia e o nível de intensidade (0-4).
    """
    
    # Se não tem token, gera dados de exemplo para teste
    if not token:
        print("⚠️  Sem token - gerando dados de exemplo")
        return generate_sample_data()
    
    query = """
    query($username: String!) {
        user(login: $username) {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                            contributionLevel
                            date
                        }
                    }
                }
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": username}},
        headers=headers
    )
    
    data = response.json()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    
    contributions = []
    for week in weeks[-WEEKS_TO_SHOW:]:
        week_data = []
        for day in week["contributionDays"]:
            # Converte NONE, FIRST_QUARTILE, etc. para 0-4
            level_map = {
                "NONE": 0,
                "FIRST_QUARTILE": 1, 
                "SECOND_QUARTILE": 2,
                "THIRD_QUARTILE": 3,
                "FOURTH_QUARTILE": 4
            }
            level = level_map.get(day["contributionLevel"], 0)
            week_data.append({
                "count": day["contributionCount"],
                "level": level,
                "date": day["date"]
            })
        contributions.append(week_data)
    
    return contributions


def generate_sample_data() -> list:
    """Gera dados fictícios para teste sem precisar de token."""
    contributions = []
    for week in range(WEEKS_TO_SHOW):
        week_data = []
        for day in range(7):
            # Gera padrão aleatório mas realista
            if random.random() < 0.3:  # 30% sem commits
                level = 0
            else:
                level = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
            week_data.append({"count": level * 2, "level": level})
        contributions.append(week_data)
    return contributions


# ============================================================
# PARTE 2: GERAR O SVG BASE (GRÁFICO DE CONTRIBUIÇÕES)
# ============================================================
def create_contribution_grid(contributions: list) -> str:
    """
    Cria o grid de quadradinhos do gráfico.
    Cada quadrado tem um ID único para podermos animar depois.
    """
    cells = []
    
    for week_idx, week in enumerate(contributions):
        for day_idx, day in enumerate(week):
            x = week_idx * (CELL_SIZE + CELL_GAP) + 40  # +40 para margem
            y = day_idx * (CELL_SIZE + CELL_GAP) + 20
            
            color = COLORS[day["level"]]
            cell_id = f"cell-{week_idx}-{day_idx}"
            
            # rx="2" deixa os cantos arredondados
            cells.append(f'''
                <rect 
                    id="{cell_id}"
                    x="{x}" 
                    y="{y}" 
                    width="{CELL_SIZE}" 
                    height="{CELL_SIZE}" 
                    fill="{color}" 
                    rx="2"
                    class="contribution-cell"
                    data-level="{day['level']}"
                />
            ''')
    
    return "\n".join(cells)


# ============================================================
# PARTE 3: CRIAR OS METEOROS COM ANIMAÇÃO
# ============================================================
def create_meteor(meteor_id: int, start_x: int, start_y: int, delay: float) -> str:
    """
    Cria um meteoro com animação de queda.
    
    ANATOMIA DE UMA ANIMAÇÃO SVG:
    - <animateTransform>: move/rotaciona o elemento
    - attributeName: qual propriedade animar (transform, opacity, etc)
    - from/to ou values: valores inicial e final
    - dur: duração da animação
    - begin: quando começa (pode ter delay)
    - repeatCount: quantas vezes repetir (indefinite = infinito)
    """
    
    # O meteoro cai na diagonal
    end_x = start_x + 100
    end_y = start_y + 150
    
    duration = random.uniform(1.5, 2.5)  # Velocidades variadas
    
    # Tamanho e brilho aleatório
    size = random.randint(3, 6)
    glow_size = size * 3
    
    return f'''
    <g id="meteor-{meteor_id}" opacity="0">
        <!-- Rastro do meteoro (blur) -->
        <line 
            x1="0" y1="0" 
            x2="-20" y2="-20"
            stroke="url(#meteor-gradient)"
            stroke-width="{size}"
            stroke-linecap="round"
            filter="url(#glow)"
        />
        
        <!-- Núcleo brilhante -->
        <circle cx="0" cy="0" r="{size/2}" fill="#ffd700">
            <!-- Pulsar o brilho -->
            <animate
                attributeName="r"
                values="{size/2};{size};{size/2}"
                dur="0.3s"
                repeatCount="indefinite"
            />
        </circle>
        
        <!-- Animação de movimento diagonal -->
        <animateTransform
            attributeName="transform"
            type="translate"
            from="{start_x},{start_y}"
            to="{end_x},{end_y}"
            dur="{duration}s"
            begin="{delay}s"
            repeatCount="indefinite"
        />
        
        <!-- Fade in quando começa, fade out no final -->
        <animate
            attributeName="opacity"
            values="0;1;1;0"
            keyTimes="0;0.1;0.8;1"
            dur="{duration}s"
            begin="{delay}s"
            repeatCount="indefinite"
        />
    </g>
    '''


def create_impact_explosion(explosion_id: int, x: int, y: int, delay: float) -> str:
    """
    Cria uma explosão quando o meteoro "impacta".
    Partículas se espalham do ponto de impacto.
    """
    particles = []
    num_particles = 6
    
    for i in range(num_particles):
        angle = (360 / num_particles) * i
        # Direção da partícula
        dx = math.cos(math.radians(angle)) * 15
        dy = math.sin(math.radians(angle)) * 15
        
        particles.append(f'''
            <circle cx="{x}" cy="{y}" r="2" fill="#ff6b35" opacity="0">
                <!-- Move a partícula para fora -->
                <animate
                    attributeName="cx"
                    from="{x}"
                    to="{x + dx}"
                    dur="0.5s"
                    begin="{delay}s"
                    repeatCount="indefinite"
                />
                <animate
                    attributeName="cy"
                    from="{y}"
                    to="{y + dy}"
                    dur="0.5s"
                    begin="{delay}s"
                    repeatCount="indefinite"
                />
                <!-- Fade out -->
                <animate
                    attributeName="opacity"
                    values="0;1;0"
                    dur="0.5s"
                    begin="{delay}s"
                    repeatCount="indefinite"
                />
                <!-- Diminui de tamanho -->
                <animate
                    attributeName="r"
                    from="3"
                    to="0"
                    dur="0.5s"
                    begin="{delay}s"
                    repeatCount="indefinite"
                />
            </circle>
        ''')
    
    return f'<g id="explosion-{explosion_id}">{" ".join(particles)}</g>'


# ============================================================
# PARTE 4: MONTAR O SVG COMPLETO
# ============================================================
def generate_svg(contributions: list) -> str:
    """Monta o SVG completo com gráfico + animações."""
    
    # Dimensões do SVG
    width = WEEKS_TO_SHOW * (CELL_SIZE + CELL_GAP) + 80
    height = 7 * (CELL_SIZE + CELL_GAP) + 60
    
    # Gera o grid de contribuições
    grid = create_contribution_grid(contributions)
    
    # Gera vários meteoros em posições aleatórias
    meteors = []
    explosions = []
    num_meteors = 8
    
    for i in range(num_meteors):
        # Posição inicial aleatória no topo
        start_x = random.randint(0, width - 100)
        start_y = random.randint(-50, -10)
        delay = random.uniform(0, 5)  # Delays diferentes para não cair tudo junto
        
        meteors.append(create_meteor(i, start_x, start_y, delay))
        
        # Explosão onde o meteoro termina
        impact_x = start_x + 100
        impact_y = start_y + 150
        impact_delay = delay + random.uniform(1.5, 2.5)  # Depois que o meteoro chega
        explosions.append(create_impact_explosion(i, impact_x, impact_y, impact_delay))
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg 
    width="{width}" 
    height="{height}" 
    viewBox="0 0 {width} {height}"
    xmlns="http://www.w3.org/2000/svg"
>
    <!-- ========== DEFINIÇÕES (filtros, gradientes) ========== -->
    <defs>
        <!-- Filtro de brilho/glow para os meteoros -->
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        
        <!-- Gradiente do rastro do meteoro -->
        <linearGradient id="meteor-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffd700;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#ff6b35;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#ff6b35;stop-opacity:0" />
        </linearGradient>
        
        <!-- Gradiente de fundo (céu noturno) -->
        <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#0d1117" />
            <stop offset="100%" style="stop-color:#161b22" />
        </linearGradient>
    </defs>
    
    <!-- ========== FUNDO ========== -->
    <rect width="100%" height="100%" fill="url(#bg-gradient)" rx="6"/>
    
    <!-- ========== TÍTULO ========== -->
    <text x="40" y="15" fill="#8b949e" font-size="11" font-family="Arial, sans-serif">
        Contributions
    </text>
    
    <!-- ========== GRID DE CONTRIBUIÇÕES ========== -->
    <g id="contribution-grid">
        {grid}
    </g>
    
    <!-- ========== METEOROS ========== -->
    <g id="meteors">
        {"".join(meteors)}
    </g>
    
    <!-- ========== EXPLOSÕES ========== -->
    <g id="explosions">
        {"".join(explosions)}
    </g>
    
    <!-- ========== LEGENDA ========== -->
    <g transform="translate({width - 150}, {height - 20})">
        <text x="0" y="0" fill="#8b949e" font-size="10" font-family="Arial">Less</text>
        <rect x="30" y="-8" width="10" height="10" fill="{COLORS[0]}" rx="2"/>
        <rect x="43" y="-8" width="10" height="10" fill="{COLORS[1]}" rx="2"/>
        <rect x="56" y="-8" width="10" height="10" fill="{COLORS[2]}" rx="2"/>
        <rect x="69" y="-8" width="10" height="10" fill="{COLORS[3]}" rx="2"/>
        <rect x="82" y="-8" width="10" height="10" fill="{COLORS[4]}" rx="2"/>
        <text x="98" y="0" fill="#8b949e" font-size="10" font-family="Arial">More</text>
    </g>
</svg>
'''
    
    return svg


# ============================================================
# PARTE 5: EXECUTAR
# ============================================================
if __name__ == "__main__":
    print("🌠 Gerando animação de meteoros...")
    
    # 1. Busca contribuições
    contributions = fetch_contributions(GITHUB_USERNAME, GITHUB_TOKEN)
    print(f"✅ {len(contributions)} semanas de contribuições carregadas")
    
    # 2. Gera o SVG
    svg = generate_svg(contributions)
    
    # 3. Salva o arquivo
    output_dir = "dist"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "meteor-contributions.svg")
    with open(output_path, "w") as f:
        f.write(svg)
    
    print(f"✅ SVG salvo em: {output_path}")
    print("🚀 Pronto!")
