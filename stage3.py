# ==========================================================
# stage3.py — Stage1과 동일한 거리, Odd-r Hex 6방향 연결
# ==========================================================
import settings    # ★ 중요: 필요할 때 직접 settings에서 읽어온다
import math

_stage3_adj = {}
stage3_connections = []


# ----------------------------------------------------------
# Odd-r HEX 방향 (열 기준으로 오프셋이 달라짐)
# ----------------------------------------------------------
EVEN_COL_DIRS = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, -1), (-1, 1)
]

ODD_COL_DIRS = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (1, -1), (1, 1)
]


# ----------------------------------------------------------
# Hex 위치 생성 (+ Stage1 동일한 spacing)
# ----------------------------------------------------------
def generate_stage3_positions(width, height):
    global _stage3_adj, stage3_connections

    positions = {}

    # ★ 항상 최신 값 읽기
    A = settings.BOMB_DISTANCE
    R = settings.BOMB_RADIUS

    center_distance = A + (2 * R)
    spacing = center_distance

    rows, cols = 4, 5

    dx = spacing * math.sqrt(3) / 2
    dy = spacing / 2

    start_x = width // 2
    start_y = height // 2

    for c in range(cols):
        for r in range(rows):
            x = start_x + (c - cols//2) * dx
            y = start_y + (r - rows//2) * spacing + (c % 2) * dy
            positions[(r, c)] = (x, y)

    # ------------------------------------------------------
    # Adjacency (Odd-r HEX)
    # ------------------------------------------------------
    adj = {node: [] for node in positions}

    for (r, c) in positions:
        dirs = EVEN_COL_DIRS if (c % 2 == 0) else ODD_COL_DIRS

        for dr, dc in dirs:
            nb = (r + dr, c + dc)
            if nb in positions:
                adj[(r, c)].append(nb)

    _stage3_adj = adj

    # 연결선 기록
    stage3_connections = []
    for a in adj:
        for b in adj[a]:
            if (b, a) not in stage3_connections:
                stage3_connections.append((a, b))

    return positions


def adjacent_nodes_stage3(node, bomb_positions):
    return _stage3_adj.get(node, [])
