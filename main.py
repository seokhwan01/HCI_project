import pygame, sys, random, math
pygame.init()

# === 화면 설정 ===
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("폭탄 제거반 EOD - 5x5 중앙 도화선")

clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 36)

# === 이미지 불러오기 ===
menu_img = pygame.image.load("menu.png").convert()
menu_img = pygame.transform.scale(menu_img, (WIDTH, HEIGHT))

start_img = pygame.image.load("start.png").convert_alpha()
start_img = pygame.transform.scale(start_img, (400, 200))
start_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

background_img = pygame.image.load("stage3_background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# === 폭탄 이미지 ===
BOMB_RADIUS = 30
black_bomb = pygame.image.load("black.png").convert_alpha()
red_bomb = pygame.image.load("red.png").convert_alpha()
black_bomb = pygame.transform.scale(black_bomb, (BOMB_RADIUS * 2, BOMB_RADIUS * 2))
red_bomb = pygame.transform.scale(red_bomb, (BOMB_RADIUS * 2, BOMB_RADIUS * 2))

# === 폭발 이미지 ===
bomb_explosion_img = pygame.image.load("bomb.png").convert_alpha()
bomb_explosion_img = pygame.transform.scale(bomb_explosion_img, (220, 220))

# === 상태 ===
state = "menu"

# === 5x5 폭탄 위치 생성 ===
grid_rows, grid_cols = 5, 5
cell_spacing = 160  # 폭탄 간 거리
grid_origin_x = WIDTH // 2 - cell_spacing * 2
grid_origin_y = HEIGHT // 2 - cell_spacing * 2

bomb_positions = {}
for r in range(grid_rows):
    for c in range(grid_cols):
        x = grid_origin_x + c * cell_spacing
        y = grid_origin_y + r * cell_spacing
        bomb_positions[(r, c)] = (x, y)

# === 인접 노드 (동서남북) ===
def adjacent_nodes(node):
    """폭탄 좌표 기준으로 상하좌우 인접 노드 반환"""
    r, c = node
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < grid_rows and 0 <= nc < grid_cols:
            yield (nr, nc)

# === 게임 변수 ===
particles = []
fuse_speed = 15.0  # 도화선 속도 약 0.44초
segment_progress = 0.0
fuse_burning = False

# 중앙 기준 폭탄
base_source = (2, 2)
current_source = base_source
previous_source = None
target_node = None

# 상태 관련
explosion_timer = 0.0
explosion_pos = None
cooldown = 0.0
game_message = "메뉴에서 시작을 누르세요!"

# === 펄스(폭탄 진동) 관련 ===
pulsing = False        # 진동 중 여부
pulse_timer = 0.0      # 진동 시간 누적
pulse_count = 0        # 진동 횟수
pulse_target = None    # 지금 진동 중인 폭탄 좌표

# === 불꽃(스파크) ===
def spawn_spark(x, y, dir_vec, count=10):
    """도화선 끝에서 불꽃 입자 생성"""
    dx, dy = dir_vec
    length = math.hypot(dx, dy)
    if length == 0: dx, dy = 1, 0
    else: dx, dy = dx/length, dy/length

    for _ in range(count):
        angle = random.uniform(-0.6, 0.6)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        vx = dx * cos_a - dy * sin_a
        vy = dx * sin_a + dy * cos_a
        vx *= random.uniform(2,6)
        vy *= random.uniform(2,6) - random.uniform(0.5,1.5)
        particles.append([
            x, y, vx, vy, random.randint(5,10),
            random.choice([(255,180,0),(255,220,100),(255,140,40)])
        ])

def update_particles():
    """입자 이동 및 수명 관리"""
    new_p = []
    for x, y, vx, vy, life, color in particles:
        if life > 0:
            x += vx; y += vy; vy += 0.3; life -= 0.3
            r = max(1, int(life/1.8))
            pygame.draw.circle(screen, color, (int(x), int(y)), r)
            new_p.append([x, y, vx, vy, life, color])
    return new_p

# === 폭탄 및 도화선 ===
def draw_bomb(pos, burning=False, dimmed=False, scale=1.0):
    """폭탄 이미지 (크기 조절 + 투명도 반영)"""
    img = red_bomb if burning else black_bomb
    img.set_alpha(120 if dimmed else 255)
    size = int(BOMB_RADIUS * 2 * scale)
    scaled_img = pygame.transform.scale(img, (size, size))
    rect = scaled_img.get_rect(center=pos)
    screen.blit(scaled_img, rect)

def draw_fuse_line(a_pos, b_pos, progress=None, active=False):
    """두 폭탄 사이 도화선 그리기"""
    sx, sy = a_pos
    ex, ey = b_pos
    pygame.draw.line(screen, (130,90,50), (sx,sy), (ex,ey), 8)
    if progress is not None:
        cx = sx + (ex-sx)*progress
        cy = sy + (ey-sy)*progress
        pygame.draw.line(screen,(240,200,80),(sx,sy),(cx,cy),6)
        if active:
            pygame.draw.circle(screen,(255,200,80),(int(cx),int(cy)),10)
            pygame.draw.circle(screen,(255,80,0),(int(cx),int(cy)),6)
            dir_vec = (sx-ex,sy-ey)
            spawn_spark(cx,cy,dir_vec,8)
        return (cx,cy)
    return None

# === 다음 목표 폭탄 ===
def choose_next_target(prev, curr):
    """현재 폭탄 기준으로 다음 폭탄을 랜덤 선택"""
    neighbors = list(adjacent_nodes(curr))
    if len(neighbors) < 4 and prev:
        neighbors = list(adjacent_nodes(prev))
    if not neighbors:
        return None
    return random.choice(neighbors)

# === 진동 시작 ===
def start_pulse_for(node):
    """해당 폭탄을 기준으로 3회 진동 시작"""
    global pulsing, pulse_timer, pulse_count, pulse_target, fuse_burning, segment_progress, game_message
    pulsing = True
    pulse_timer = 0.0
    pulse_count = 0
    pulse_target = node
    fuse_burning = False
    segment_progress = 0.0
    game_message = f"💣 {node} 폭탄 점화 준비 중..."

# === 라운드 시작 ===
def start_new_round():
    """게임 시작 시 진동 후 도화선 점화"""
    global current_source, previous_source, target_node
    previous_source = None
    current_source = (2,2)
    target_node = choose_next_target(previous_source, current_source)
    start_pulse_for(current_source)

# === 폭발 처리 ===
def explode(node):
    global fuse_burning, cooldown, explosion_timer, explosion_pos
    global previous_source, current_source, target_node, game_message

    fuse_burning = False
    cooldown = 1.2
    explosion_timer = 0.6
    explosion_pos = bomb_positions[node]

    # 가장자리라면 기준 폭탄으로 복귀
    r, c = node
    if r == 0 or c == 0 or r == grid_rows-1 or c == grid_cols-1:
        current_source = (2,2)
        previous_source = None
        game_message = f"{node} 폭발! 기준 폭탄 (2,2)로 복귀!"
    else:
        previous_source = current_source
        current_source = node
        game_message = f"{node} 폭발! 다음 목표 선택 중..."

    target_node = choose_next_target(previous_source, current_source)
    start_pulse_for(current_source)

# === 해제 처리 ===
def defuse():
    global fuse_burning, cooldown, game_message
    global previous_source, current_source, target_node

    fuse_burning = False
    cooldown = 1.0

    # 가장자리라면 기준 폭탄으로 복귀
    r, c = target_node
    if r == 0 or c == 0 or r == grid_rows-1 or c == grid_cols-1:
        current_source = (2,2)
        previous_source = None
        game_message = f"✅ 해제 성공! 기준 폭탄 (2,2)로 복귀!"
    else:
        previous_source = current_source
        current_source = target_node
        game_message = f"✅ 해제 성공! 다음 목표 선택 중..."

    target_node = choose_next_target(previous_source, current_source)
    start_pulse_for(current_source)

# === 일시정지 버튼 ===
pause_font = pygame.font.SysFont("malgungothic", 50)
resume_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 80)
quit_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 40, 300, 80)

# === 메인 루프 ===
running = True
while running:
    dt = clock.tick(60)/1000.0

    # === 이벤트 처리 ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.event.set_grab(False)
            pygame.quit(); sys.exit()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state == "game":
                state = "pause"
                pygame.event.set_grab(False)  # 마우스 해제
            elif state == "pause":
                state = "game"
                pygame.event.set_grab(True)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "menu":
                if start_rect.collidepoint(event.pos):
                    state = "game"
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(True)
                    start_new_round()

            elif state == "game" and fuse_burning:
                mx,my = event.pos
                tx,ty = bomb_positions[target_node]
                if math.hypot(mx-tx,my-ty) <= BOMB_RADIUS:
                    defuse()
                else:
                    game_message = "❌ 잘못된 폭탄 클릭!"

            elif state == "pause":
                if resume_button.collidepoint(event.pos):
                    state = "game"
                    pygame.event.set_grab(True)
                elif quit_button.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

    # === 메뉴 ===
    if state == "menu":
        screen.blit(menu_img,(0,0))
        screen.blit(start_img,start_rect)
        pygame.display.flip()
        continue

    # === 일시정지 화면 ===
    if state == "pause":
        screen.blit(background_img, (0,0))
        pygame.draw.rect(screen, (0,0,0,150), (0,0,WIDTH,HEIGHT))
        pygame.draw.rect(screen, (200,200,200), resume_button, border_radius=15)
        pygame.draw.rect(screen, (200,100,100), quit_button, border_radius=15)

        resume_text = pause_font.render("▶ 계속하기", True, (0,0,0))
        quit_text = pause_font.render("종료하기", True, (0,0,0))
        screen.blit(resume_text, (resume_button.centerx - resume_text.get_width()//2, resume_button.centery - resume_text.get_height()//2))
        screen.blit(quit_text, (quit_button.centerx - quit_text.get_width()//2, quit_button.centery - quit_text.get_height()//2))

        pygame.display.flip()
        continue

    # === 게임 화면 ===
    screen.blit(background_img,(0,0))

    for nb in adjacent_nodes(current_source):
        draw_fuse_line(bomb_positions[current_source], bomb_positions[nb])

    if fuse_burning and target_node:
        a_pos = bomb_positions[current_source]
        b_pos = bomb_positions[target_node]
        draw_fuse_line(a_pos,b_pos,progress=segment_progress,active=True)
        segment_progress += fuse_speed * dt * 0.15
        if segment_progress >= 1:
            explode(target_node)

    active_nodes = {current_source, *adjacent_nodes(current_source)}
    for node, pos in bomb_positions.items():
        burning = fuse_burning and node == target_node
        dimmed = node not in active_nodes
        scale = 1.0
        if pulsing and node == pulse_target:
            scale = 1.0 + 0.25 * math.sin(pulse_timer)
        draw_bomb(pos, burning, dimmed, scale)

    if pulsing:
        pulse_timer += dt * 10.0
        if pulse_timer >= math.pi * 2:
            pulse_timer = 0
            pulse_count += 1
            if pulse_count >= 3:
                pulsing = False
                fuse_burning = True
                segment_progress = 0.0
                game_message = f"{current_source} → {target_node} 도화선 점화!"

    if explosion_timer>0 and explosion_pos:
        rect = bomb_explosion_img.get_rect(center=explosion_pos)
        screen.blit(bomb_explosion_img,rect)
        explosion_timer-=dt

    particles = update_particles()
    text = font.render(game_message,True,(10,10,10))
    screen.blit(text,(WIDTH//2 - text.get_width()//2, 40))
    pygame.display.flip()
