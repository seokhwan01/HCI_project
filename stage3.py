# ==========================================================
# stage3.py — 5x5 육각형 구조 (모든 중심이 연결 6개 가능)
# ==========================================================

def generate_stage3_positions(WIDTH, HEIGHT):
    positions = {}

    spacing = 120
    rows = 5
    cols = 5

    start_x = WIDTH // 2 - spacing * 2
    start_y = HEIGHT // 2 - spacing * 2

    for c in range(cols):
        offset_y = spacing * 0.5 if (c % 2 == 1) else 0

        for r in range(rows):
            x = start_x + c * spacing
            y = start_y + r * spacing + offset_y
            positions[(r, c)] = (x, y)

    return positions


def adjacent_nodes_stage3(node, bomb_positions):
    r, c = node

    # even-q vertical layout
    if c % 2 == 0:
        dirs = [(-1, 0), (1, 0),
                (0, -1), (0, 1),
                (-1, -1), (-1, 1)]
    else:
        dirs = [(-1, 0), (1, 0),
                (0, -1), (0, 1),
                (1, -1), (1, 1)]

    for dr, dc in dirs:
        nb = (r + dr, c + dc)
        if nb in bomb_positions:
            yield nb
