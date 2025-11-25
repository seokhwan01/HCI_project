# ==========================================================
# stage2.py — Stage2 전용: 5×5 격자 + 십자형(4방향) 연결
# ==========================================================

import settings   # ★ 가장 중요! 항상 최신 값 사용

# ----------------------------------------------------------
# 5×5 정중앙 격자 배치 생성
# ----------------------------------------------------------
def generate_stage2_positions():

    A = settings.BOMB_DISTANCE
    R = settings.BOMB_RADIUS

    center_distance = A + (2 * R)
    spacing = center_distance

    rows, cols = 4, 5

    origin_x = settings.WIDTH // 2 - spacing * 2
    origin_y = settings.HEIGHT // 2 - spacing * 2

    positions = {}

    for r in range(rows):
        for c in range(cols):
            x = origin_x + c * spacing
            y = origin_y + r * spacing
            positions[(r, c)] = (x, y)

    return positions


# ----------------------------------------------------------
# ✨ Stage2 핵심: 오직 4방향(상하좌우)만 adjacency 허용
# ----------------------------------------------------------
def adjacent_nodes_stage2(node, bomb_positions):

    r, c = node

    cross_offsets = [
        (-1, 0),  # 위
        (1, 0),   # 아래
        (0, -1),  # 왼쪽
        (0, 1),   # 오른쪽
    ]

    for dr, dc in cross_offsets:
        nxt = (r + dr, c + dc)
        if nxt in bomb_positions:
            yield nxt
