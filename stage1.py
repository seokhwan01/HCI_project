# ==========================================================
# stage1.py — settings 값 자동 반영 버전
# ==========================================================
import math
import settings   # ★ settings 전체 import (중요!)

stage1_connections = []
_stage1_adj = {}

def generate_stage1_positions(WIDTH, HEIGHT):
    global stage1_connections, _stage1_adj

    positions = {}

    # ★ apply_condition()이 settings 값을 바꾸면 즉시 반영됨
    A = settings.BOMB_DISTANCE
    R = settings.BOMB_RADIUS

    # 표면 간 거리 A → 중심 간 거리 = A + 2R
    spacing = A + (2 * R)

    rows = 4
    cols = 5

    # 정삼각형 기반 spacing
    dx = spacing * math.sqrt(3) / 2
    dy = spacing / 2

    start_x = WIDTH // 2
    start_y = HEIGHT // 2

    for c in range(cols):
        for r in range(rows):
            x = start_x + (c - cols//2) * dx
            y = start_y + (r - rows//2) * spacing + (c % 2) * dy
            positions[(r, c)] = (x, y)

    # adjacency 그대로 유지
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
