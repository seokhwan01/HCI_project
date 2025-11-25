# ==========================================================
# stage1.py — adjacency 유지 + 도화선 거리 정확히 spacing
# ==========================================================
from settings import BOMB_DISTANCE,BOMB_RADIUS
import math

stage1_connections = []
_stage1_adj = {}


def generate_stage1_positions(WIDTH, HEIGHT):
    global stage1_connections, _stage1_adj

    positions = {}
    # spacing = BOMB_DISTANCE  # 140
    A = BOMB_DISTANCE  # 네가 설정한 실험용 A
    center_distance = A + (2 * BOMB_RADIUS)
    spacing = center_distance
    rows = 4
    cols = 5

    # 정삼각형 기반 spacing
    dx = spacing * math.sqrt(3) / 2   # 121.24 px
    dy = spacing / 2                  # 70 px

    start_x = WIDTH // 2
    start_y = HEIGHT // 2

    for c in range(cols):
        for r in range(rows):

            # 시각적 형태는 유지되지만 대각선 길이를 맞춘 형태
            x = start_x + (c - cols//2) * dx
            y = start_y + (r - rows//2) * spacing + (c % 2) * dy

            positions[(r, c)] = (x, y)

    # === adjacency (너의 원래 로직 그대로) ===
    adj = {node: [] for node in positions}

    for (r, c) in positions:

        if c % 2 == 0:
            dirs = [(-1, 0), (0, -1), (0, 1)]
        else:
            dirs = [(-1, 0), (1, -1), (1, 1)]

        for dr, dc in dirs:
            nb = (r + dr, c + dc)
            if nb in positions:
                adj[(r, c)].append(nb)

    _stage1_adj = adj

    stage1_connections = []
    for a in adj:
        for b in adj[a]:
            if (b, a) not in stage1_connections:
                stage1_connections.append((a, b))

    return positions



def adjacent_nodes_stage1(node, bomb_positions):
    return _stage1_adj.get(node, [])
