import requests
import random
import math
import os

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "giovanicavila")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

CELL_SIZE = 11
CELL_GAP = 3
WEEKS_TO_SHOW = 53


def fetch_contributions(username: str, token: str) -> list:
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
    contributions = []
    for week in range(WEEKS_TO_SHOW):
        week_data = []
        for day in range(7):
            if random.random() < 0.3:
                level = 0
            else:
                level = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
            week_data.append({"count": level * 2, "level": level})
        contributions.append(week_data)
    return contributions


def create_contribution_grid(contributions: list) -> str:
    cells = []
    
    for week_idx, week in enumerate(contributions):
        for day_idx, day in enumerate(week):
            x = week_idx * (CELL_SIZE + CELL_GAP) + 40
            y = day_idx * (CELL_SIZE + CELL_GAP) + 20
            
            color = COLORS[day["level"]]
            cell_id = f"cell-{week_idx}-{day_idx}"
            
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


def create_meteor(meteor_id: int, start_x: int, start_y: int, delay: float) -> str:
    end_x = start_x + 100
    end_y = start_y + 150
    duration = random.uniform(1.5, 2.5)
    size = random.randint(3, 6)
    
    return f'''
    <g id="meteor-{meteor_id}" opacity="0">
        <line 
            x1="0" y1="0" 
            x2="-20" y2="-20"
            stroke="url(#meteor-gradient)"
            stroke-width="{size}"
            stroke-linecap="round"
            filter="url(#glow)"
        />
        <circle cx="0" cy="0" r="{size/2}" fill="#ffd700">
            <animate
                attributeName="r"
                values="{size/2};{size};{size/2}"
                dur="0.3s"
                repeatCount="indefinite"
            />
        </circle>
        <animateTransform
            attributeName="transform"
            type="translate"
            from="{start_x},{start_y}"
            to="{end_x},{end_y}"
            dur="{duration}s"
            begin="{delay}s"
            repeatCount="indefinite"
        />
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
    particles = []
    num_particles = 6
    
    for i in range(num_particles):
        angle = (360 / num_particles) * i
        dx = math.cos(math.radians(angle)) * 15
        dy = math.sin(math.radians(angle)) * 15
        
        particles.append(f'''
            <circle cx="{x}" cy="{y}" r="2" fill="#ff6b35" opacity="0">
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
                <animate
                    attributeName="opacity"
                    values="0;1;0"
                    dur="0.5s"
                    begin="{delay}s"
                    repeatCount="indefinite"
                />
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


def generate_svg(contributions: list) -> str:
    width = WEEKS_TO_SHOW * (CELL_SIZE + CELL_GAP) + 80
    height = 7 * (CELL_SIZE + CELL_GAP) + 60
    
    grid = create_contribution_grid(contributions)
    
    meteors = []
    explosions = []
    num_meteors = 8
    
    for i in range(num_meteors):
        start_x = random.randint(0, width - 100)
        start_y = random.randint(-50, -10)
        delay = random.uniform(0, 5)
        
        meteors.append(create_meteor(i, start_x, start_y, delay))
        
        impact_x = start_x + 100
        impact_y = start_y + 150
        impact_delay = delay + random.uniform(1.5, 2.5)
        explosions.append(create_impact_explosion(i, impact_x, impact_y, impact_delay))
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg 
    width="{width}" 
    height="{height}" 
    viewBox="0 0 {width} {height}"
    xmlns="http://www.w3.org/2000/svg"
>
    <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        
        <linearGradient id="meteor-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffd700;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#ff6b35;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#ff6b35;stop-opacity:0" />
        </linearGradient>
        
        <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#0d1117" />
            <stop offset="100%" style="stop-color:#161b22" />
        </linearGradient>
    </defs>
    
    <rect width="100%" height="100%" fill="url(#bg-gradient)" rx="6"/>
    
    <text x="40" y="15" fill="#8b949e" font-size="11" font-family="Arial, sans-serif">
        Contributions
    </text>
    
    <g id="contribution-grid">
        {grid}
    </g>
    
    <g id="meteors">
        {"".join(meteors)}
    </g>
    
    <g id="explosions">
        {"".join(explosions)}
    </g>
    
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


if __name__ == "__main__":
    print("🌠 Gerando animação de meteoros...")
    
    contributions = fetch_contributions(GITHUB_USERNAME, GITHUB_TOKEN)
    print(f"✅ {len(contributions)} semanas de contribuições carregadas")
    
    svg = generate_svg(contributions)
    
    output_dir = "dist"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "meteor-contributions.svg")
    with open(output_path, "w") as f:
        f.write(svg)
    
    print(f"✅ SVG salvo em: {output_path}")
