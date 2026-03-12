import requests
import random
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

CELL_SIZE = 14
CELL_GAP = 4
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


def count_commits(contributions: list) -> int:
    count = 0
    for week in contributions:
        for day in week:
            if day["level"] > 0:
                count += 1
    return count


def create_contribution_grid(contributions: list, height: int, total_commits: int) -> str:
    cells = []
    fall_index = 0
    
    delay_between = 0.08
    fall_duration = 1.5
    pause_at_end = 2.0
    
    total_cycle = (total_commits * delay_between) + fall_duration + pause_at_end
    
    for week_idx, week in enumerate(contributions):
        for day_idx, day in enumerate(week):
            x = week_idx * (CELL_SIZE + CELL_GAP) + 50
            y = day_idx * (CELL_SIZE + CELL_GAP) + 30
            
            level = day["level"]
            color = COLORS[level]
            
            if level > 0:
                delay = fall_index * delay_between
                fall_distance = height - y + 50
                rotation = random.randint(-45, 45)
                
                cells.append(f'''
                <rect 
                    x="{x}" 
                    y="{y}" 
                    width="{CELL_SIZE}" 
                    height="{CELL_SIZE}" 
                    fill="{color}" 
                    rx="3"
                >
                    <animate
                        attributeName="y"
                        values="{y};{y + fall_distance};{y}"
                        keyTimes="0;{fall_duration/total_cycle:.4f};1"
                        dur="{total_cycle}s"
                        begin="{delay}s"
                        repeatCount="indefinite"
                        calcMode="spline"
                        keySplines="0.4 0 1 1; 0 0 0.2 1"
                    />
                    <animate
                        attributeName="opacity"
                        values="1;0;0;1"
                        keyTimes="0;{fall_duration/total_cycle:.4f};{(total_cycle - 0.3)/total_cycle:.4f};1"
                        dur="{total_cycle}s"
                        begin="{delay}s"
                        repeatCount="indefinite"
                    />
                </rect>
                ''')
                fall_index += 1
            else:
                cells.append(f'''
                <rect 
                    x="{x}" 
                    y="{y}" 
                    width="{CELL_SIZE}" 
                    height="{CELL_SIZE}" 
                    fill="{color}" 
                    rx="3"
                />
                ''')
    
    return "\n".join(cells)


def generate_svg(contributions: list) -> str:
    width = WEEKS_TO_SHOW * (CELL_SIZE + CELL_GAP) + 100
    height = 7 * (CELL_SIZE + CELL_GAP) + 80
    
    total_commits = count_commits(contributions)
    grid = create_contribution_grid(contributions, height, total_commits)
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg 
    width="{width}" 
    height="{height}" 
    viewBox="0 0 {width} {height}"
    xmlns="http://www.w3.org/2000/svg"
>
    <defs>
        <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#0d1117" />
            <stop offset="100%" style="stop-color:#161b22" />
        </linearGradient>
    </defs>
    
    <rect width="100%" height="100%" fill="url(#bg-gradient)" rx="8"/>
    
    <text x="50" y="22" fill="#8b949e" font-size="12" font-family="Arial, sans-serif">
        Contributions
    </text>
    
    <g id="contribution-grid">
        {grid}
    </g>
    
    <g transform="translate({width - 170}, {height - 25})">
        <text x="0" y="0" fill="#8b949e" font-size="11" font-family="Arial">Less</text>
        <rect x="35" y="-10" width="12" height="12" fill="{COLORS[0]}" rx="3"/>
        <rect x="51" y="-10" width="12" height="12" fill="{COLORS[1]}" rx="3"/>
        <rect x="67" y="-10" width="12" height="12" fill="{COLORS[2]}" rx="3"/>
        <rect x="83" y="-10" width="12" height="12" fill="{COLORS[3]}" rx="3"/>
        <rect x="99" y="-10" width="12" height="12" fill="{COLORS[4]}" rx="3"/>
        <text x="118" y="0" fill="#8b949e" font-size="11" font-family="Arial">More</text>
    </g>
</svg>
'''
    
    return svg


if __name__ == "__main__":
    print("🧱 Gerando animação de desmoronamento...")
    
    contributions = fetch_contributions(GITHUB_USERNAME, GITHUB_TOKEN)
    print(f"✅ {len(contributions)} semanas de contribuições carregadas")
    
    svg = generate_svg(contributions)
    
    output_dir = "dist"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "meteor-contributions.svg")
    with open(output_path, "w") as f:
        f.write(svg)
    
    print(f"✅ SVG salvo em: {output_path}")
