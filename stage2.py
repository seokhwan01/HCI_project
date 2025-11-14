from settings import WIDTH, HEIGHT

def generate_stage2_positions(spacing=160):
    positions = {}
    rows, cols = 5, 5
    origin_x = WIDTH//2 - spacing*2
    origin_y = HEIGHT//2 - spacing*2

    for r in range(rows):
        for c in range(cols):
            positions[(r,c)] = (origin_x + c*spacing, origin_y + r*spacing)
    return positions

def adjacent_nodes_stage2(node, bomb_positions): 
    r, c = node
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        new = (r+dr, c+dc)
        if new in bomb_positions:
            yield new
