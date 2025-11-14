import pygame, sys, math
pygame.init()

# === 화면 설정 ===
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("폭탄 배치 테스트 (세로형 벌집 구조)")

clock = pygame.time.Clock()

BOMB_RADIUS = 25
spacing = 120  # 폭탄 간 거리

# === 폭탄 위치 생성 (세로 방향 육각형)
def generate_bomb_positions():
    positions = {}
    cols = 5
    for c in range(cols):
        rows = 5 if c % 2 == 0 else 4  # 홀짝 열마다 행 수 다르게
        offset_y = 0 if c % 2 == 0 else spacing * 0.5
        for r in range(rows):
            x = WIDTH // 2 - spacing * 2 + c * spacing
            y = HEIGHT // 2 - spacing * 2 + r * spacing + offset_y
            positions[(r, c)] = (x, y)
    return positions

bomb_positions = generate_bomb_positions()

# === 인접 노드 (세로 육각형 구조)
def adjacent_nodes(node):
    r, c = node
    if c % 2 == 0:
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
    else:
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]
    for dr, dc in dirs:
        if (r + dr, c + dc) in bomb_positions:
            yield (r + dr, c + dc)

# === 메인 루프 ===
running = True
while running:
    dt = clock.tick(60)
    screen.fill((240, 240, 240))

    # 도화선
    for node, pos in bomb_positions.items():
        for nb in adjacent_nodes(node):
            nb_pos = bomb_positions[nb]
            pygame.draw.line(screen, (80, 80, 80), pos, nb_pos, 3)

    # 폭탄
    for node, pos in bomb_positions.items():
        pygame.draw.circle(screen, (0, 0, 0), pos, BOMB_RADIUS + 3)
        pygame.draw.circle(screen, (255, 100, 100), pos, BOMB_RADIUS)

    # ESC로 종료
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    pygame.display.flip()
