# ==========================================================
# main_stage3_test.py — STAGE 3 ONLY TEST MODE
# ==========================================================
import pygame, sys
from settings import WIDTH, HEIGHT, FPS, small_font, pause_font

from assets import load_ui_images, load_bomb_images, load_background
from stage3 import generate_stage3_positions, adjacent_nodes_stage3

from logic.base_logic import init_game_state
from logic.stage3_logic import (
    start_new_round_stage3, explode_stage3, handle_defuse_success_stage3
)

from renderer import render_game
from events import handle_events


# ==========================================================
# 초기 설정
# ==========================================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("💣 Stage 3 테스트")


# ==========================================================
# UI / 버튼
# ==========================================================
black_bomb, red_bomb, exp_img = load_bomb_images()
gameover_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 40, 300, 80)


# ==========================================================
# Stage 3만 실행용 초기값
# ==========================================================
state = init_game_state()
state["round_count"] = 1
state["MAX_ROUNDS"] = 10     # Stage3 10라운드

stage = 3
source3 = (2, 2)

background_img = load_background(3)
bomb_positions = generate_stage3_positions(WIDTH, HEIGHT)
stage3_adj = {node: list(adjacent_nodes_stage3(node, bomb_positions)) for node in bomb_positions}

start_new_round_stage3(state, bomb_positions, stage3_adj, source3)


# ==========================================================
# 메인 루프
# ==========================================================
while True:

    dt = clock.tick(FPS) / 1000.0
    state["dt"] = dt

    # ---------------------- 이벤트 ----------------------
    for e in pygame.event.get():

        # 게임 종료 화면이면 버튼 클릭으로 종료
        if state.get("game_finished"):
            if e.type == pygame.MOUSEBUTTONDOWN:
                if gameover_btn.collidepoint(e.pos):
                    pygame.quit(); sys.exit()

        # 일반 클릭 → 이벤트 처리
        result = handle_events(
            e, state, stage, bomb_positions,
            None, None, None, None,
            None, None, None
        )

        if result == "quit":
            pygame.quit(); sys.exit()


    # ---------------------- 펄스 시스템 ----------------------
    if state["pulse_phase"] == 1:
        state["pulse_delay"] -= dt
        if state["pulse_delay"] <= 0:
            state["pulse_phase"] = 2
            state["pulsing"] = True
            state["pulse_target"] = state["current_source"]
            state["pulse_timer"] = 0
            print(f"⚡ 펄스 시작 ({state['pulse_count']+1}/3)")

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
            print("↺ 다음 펄스 준비")
        else:
            print("🔥 펄스 완료 → 도화선 시작")
            state["pulse_phase"] = 0
            state["pulse_count"] = 0
            state["fuse_burning"] = True
            state["segment_progress"] = 0


    # ---------------------- 폭발 타이머 ----------------------
    if state["explosion_timer"] > 0:
        state["explosion_timer"] -= dt
    else:
        state["exploded_this_frame"] = False


    # ---------------------- 게임 종료 화면 ----------------------
    if state.get("game_finished"):
        screen.fill((0,0,0))

        txt = small_font.render(" GAME CLEAR!", True, (255,255,255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 80))

        pygame.draw.rect(screen, (200,50,50), gameover_btn, border_radius=18)
        t = small_font.render("게임 종료", True, (255,255,255))
        screen.blit(t, (gameover_btn.centerx - t.get_width()//2,
                        gameover_btn.centery - t.get_height()//2))

        pygame.display.flip()
        continue


    # ---------------------- 렌더링 ----------------------
    render_game(
    screen, background_img, stage, bomb_positions,
    black_bomb, red_bomb, exp_img, small_font,
    WIDTH, HEIGHT, state,
    None, None, None, stage3_adj
)



