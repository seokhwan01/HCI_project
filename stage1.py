import math

# === Stage1 폭탄 구조 ===
layout = [
    [0,0,1,0,1,0,0],
    [1,0,1,0,1,0,1],
    [0,1,0,1,0,1,0],
    [0,1,0,1,0,1,0],
    [1,0,1,0,1,0,1],
    [0,0,1,0,1,0,0]
]

ROWS = len(layout)
COLS = len(layout[0])
SPACING = 140
OFFSET_X = 40
OFFSET_Y = 30

# === Stage1 도화선 연결 ===
stage1_connections = [
    # 상단부
    ((0,2),(1,2)), ((0,4),(1,4)),

    # 중간부
    ((1,0),(2,1)), ((1,2),(2,1)), ((1,2),(2,3)),
    ((1,4),(2,3)), ((1,4),(2,5)), ((1,6),(2,5)),

    ((2,1),(3,1)), ((2,3),(3,3)), ((2,5),(3,5)),

    ((3,1),(4,0)), ((3,1),(4,2)),
    ((3,3),(4,2)), ((3,3),(4,4)),
    ((3,5),(4,4)), ((3,5),(4,6)),

    # 하단부
    ((4,2),(5,2)), ((4,4),(5,4)),
]

# ----------------------------------------------------------
# 폭탄 좌표 생성
# ----------------------------------------------------------
def generate_stage1_positions(WIDTH, HEIGHT):
    positions = {}

    H_SPACING = SPACING
    V_SPACING = SPACING * math.sqrt(3) / 2  # 육각형 세로 거리

    max_col_offset = (COLS - 1) * (H_SPACING * 0.5)
    pattern_width = max_col_offset + H_SPACING
    pattern_height = (ROWS - 1) * V_SPACING + H_SPACING * 0.5

    start_x = WIDTH / 2 - pattern_width / 2 + OFFSET_X
    start_y = HEIGHT / 2 - pattern_height / 2 + OFFSET_Y

    for r in range(ROWS):
        for c in range(COLS):
            if layout[r][c] == 1:
                x = start_x + c * (H_SPACING * 0.5)
                y = start_y + r * V_SPACING
                positions[(r, c)] = (x, y)

    return positions


# ----------------------------------------------------------
# adjacency 생성 (자기 자신 연결 제거)
# ----------------------------------------------------------
def adjacent_nodes_stage1(node, bomb_positions):
    """현재 폭탄 기준으로 stage1_connections을 따라 연결된 인접 노드 반환"""
    from stage1 import stage1_connections  # 내부 import (순환 참조 방지)
    r_list = []
    for a, b in stage1_connections:
        if a == node and b in bomb_positions:
            r_list.append(b)
        elif b == node and a in bomb_positions:
            r_list.append(a)
    return r_list
