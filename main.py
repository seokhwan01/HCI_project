# ==========================================================
# main.py — FIXED + FULL COMMENTS
# ==========================================================
import pygame, sys
from settings import WIDTH, HEIGHT, FPS, small_font, pause_font
from assets import load_ui_images, load_bomb_images, load_background

# Stage modules
from stage1 import generate_stage1_positions, stage1_connections, adjacent_nodes_stage1
from stage2 import generate_stage2_positions, adjacent_nodes_stage2
from stage3 import generate_stage3_positions, adjacent_nodes_stage3

# Logic
from logic.base_logic import init_game_state
from logic.stage1_logic import start_new_round_stage1
from logic.stage2_logic import start_new_round_stage2
from logic.stage3_logic import start_new_round_stage3

# Renderer / Events
from renderer import render_menu, render_pause, render_game
from events import handle_events


# ==========================================================
# Pygame 초기화
# ==========================================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("💣 폭탄 제거반 EOD")


# ==========================================================
# UI / 버튼
# ==========================================================
menu_img, start_img = load_ui_images()
black_bomb, red_bomb, exp_img = load_bomb_images()

start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))

resume_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 80)
menu_btn   = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 60, 300, 80)
quit_btn   = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 80)

gameover_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 40, 300, 80)


# ==========================================================
# 초기 상태 — 반드시 state["state"] == "menu" 여야 함
# ==========================================================
state = init_game_state()
stage = 1

source1 = (2, 3)
source2 = (2, 2)
source3 = (2, 2)

background_img = load_background(stage)

bomb_positions = generate_stage1_positions(WIDTH, HEIGHT)
stage1_adj = {node: adjacent_nodes_stage1(node, bomb_positions) for node in bomb_positions}


# ==========================================================
# 메인 루프
# ==========================================================
while True:

    dt = clock.tick(FPS) / 1000.0
    state["dt"] = dt

    # ------------------------------------------------------
    # 이벤트 처리
    # ------------------------------------------------------
    for e in pygame.event.get():

        if state.get("game_finished") and not state.get("gameover_wait"):
            if e.type == pygame.MOUSEBUTTONDOWN and gameover_btn.collidepoint(e.pos):
                pygame.quit(); sys.exit()

        result = handle_events(
            e, state, stage, bomb_positions,
            start_rect, resume_btn, menu_btn, quit_btn,
            source1, source2, stage1_adj
        )

        if result == "quit":
            pygame.quit(); sys.exit()

        if result == "start_game":

            pygame.event.set_grab(True)
            pygame.mouse.set_visible(True)

            stage = 1
            state = init_game_state()
            state["state"] = "game"

            bomb_positions = generate_stage1_positions(WIDTH, HEIGHT)
            stage1_adj = {
                node: adjacent_nodes_stage1(node, bomb_positions)
                for node in bomb_positions
            }

            background_img = load_background(stage)
            start_new_round_stage1(state, bomb_positions, stage1_adj, source1)

        if result == "menu":
            stage = 1
            state = init_game_state()
            background_img = load_background(stage)


    # ------------------------------------------------------
    # 메뉴 화면
    # ------------------------------------------------------
    if state["state"] == "menu":
        render_menu(screen, menu_img, start_img, start_rect)
        pygame.display.flip()
        continue

    # ------------------------------------------------------
    # 일시정지 화면
    # ------------------------------------------------------
    if state["state"] == "pause":
        render_pause(
            screen,
            background_img,
            WIDTH,
            HEIGHT,
            pause_font,
            resume_btn,
            menu_btn,
            quit_btn
        )
        pygame.display.flip()
        continue

    # ------------------------------------------------------
    # 게임 클리어 화면 처리
    # ------------------------------------------------------
    if state.get("game_finished"):

        if not state.get("gameover_wait"):
            state["gameover_wait"] = 2.0
        else:
            state["gameover_wait"] -= dt
            if state["gameover_wait"] <= 0:
                state["gameover_wait"] = None

        screen.fill((0, 0, 0))
        text = small_font.render("GAME CLEAR!", True, (255,255,255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))

        if state.get("gameover_wait") is None:
            pygame.draw.rect(screen, (200,50,50), gameover_btn, border_radius=18)
            txt = small_font.render("게임 종료", True, (255,255,255))
            screen.blit(txt, (gameover_btn.centerx - txt.get_width()//2,
                              gameover_btn.centery - txt.get_height()//2))

        pygame.display.flip()
        continue



    # ======================================================
    # ★★★ 여기서부터 추가된 Stage 전환 + 종료 처리 ★★★
    # ======================================================

    # ------------------------------------------------------
    # ★ Stage3 라운드 종료 → 게임 클리어 처리
    # ------------------------------------------------------
    if stage == 3 and state["round_count"] > state["MAX_ROUNDS"]:   # ★ 추가됨

        if not state.get("game_finished"):
            state["game_finished"] = True
            state["gameover_wait"] = 2.0     # 2초 대기 후 종료 화면

        continue


    # ------------------------------------------------------
    # ★ Stage1 / Stage2 → 다음 스테이지 전환 처리
    # ------------------------------------------------------
    if stage in (1, 2) and state["waiting_stage_change"]:          # ★ 추가됨

        state["stage_transition_timer"] -= dt

        if state["stage_transition_timer"] <= 0:

            state["waiting_stage_change"] = False

            if stage == 1:      # Stage 1 → Stage 2
                stage = 2
                bomb_positions = generate_stage2_positions()
                stage2_adj = {
                    node: list(adjacent_nodes_stage2(node, bomb_positions))
                    for node in bomb_positions
                }
                background_img = load_background(stage)
                state["round_count"] = 1
                start_new_round_stage2(state, bomb_positions, stage2_adj, source2)

            elif stage == 2:    # Stage 2 → Stage 3
                stage = 3
                bomb_positions = generate_stage3_positions(WIDTH, HEIGHT)
                stage3_adj = {
                    node: list(adjacent_nodes_stage3(node, bomb_positions))
                    for node in bomb_positions
                }
                background_img = load_background(stage)
                state["round_count"] = 1
                start_new_round_stage3(state, bomb_positions, stage3_adj, source3)

        continue

    # ======================================================
    # ★★★ 추가 블록 끝 ★★★
    # ======================================================



    # ------------------------------------------------------
    # ★★★ 펄스 FSM (기존 코드 그대로 유지) ★★★
    # ------------------------------------------------------
    if state["pulse_phase"] == 1:
        state["pulse_delay"] -= dt
        if state["pulse_delay"] <= 0:
            state["pulse_phase"] = 2
            state["pulsing"] = True
            state["pulse_timer"] = 0
            state["pulse_target"] = state["current_source"]

    elif state["pulse_phase"] == 2:
        state["pulse_timer"] += dt
        if state["pulse_timer"] >= state["pulse_duration"]:
            state["pulse_phase"] = 3
            state["pulsing"] = False

    elif state["pulse_phase"] == 3:
        state["pulse_count"] += 1
        if state["pulse_count"] < 3:
            state["pulse_phase"] = 1
            state["pulse_delay"] = 0.25
        else:
            state["pulse_phase"] = 4

    elif state["pulse_phase"] == 4:
        state["pulse_phase"] = 5
        state["fuse_burning"] = True
        state["segment_progress"] = 0


    # ------------------------------------------------------
    # 게임 화면 렌더링
    # ------------------------------------------------------
    render_game(
        screen,
        background_img,
        stage,
        bomb_positions,
        black_bomb,
        red_bomb,
        exp_img,
        small_font,
        WIDTH,
        HEIGHT,
        state,
        stage1_connections,
        stage1_adj,
        adjacent_nodes_stage2,
        stage3_adj if stage == 3 else {}
    )

    pygame.display.flip()
