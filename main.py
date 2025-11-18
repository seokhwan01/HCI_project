# ==========================================================
# main.py — FINAL CLEAN VERSION (Stage Start + Transition + End Screens)
# ==========================================================
import pygame, sys
from settings import WIDTH, HEIGHT, FPS, small_font, pause_font
from assets import load_assets

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
# Load ALL assets
# ==========================================================
assets = load_assets()

menu_img   = assets["menu"]
start_img  = assets["start"]
exit_img   = assets["exit"]

black_bomb  = assets["black_bomb"]
red_bomb    = assets["red_bomb"]
exp_img     = assets["explosion"]
success_img = assets["success"]

start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))
exit_rect  = exit_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))


# ==========================================================
# ⭐ Pause 버튼 Rect
# ==========================================================
resume_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 80)
menu_btn   = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 60, 300, 80)
quit_btn   = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 80)


# ==========================================================
# 초기 상태
# ==========================================================
state = init_game_state()
stage = 1

source1 = (2, 2)
source2 = (2, 2)
source3 = (2, 2)

background_img = assets["stage1_bg"]


# ==========================================================
# Stage1 초기 배치
# ==========================================================
bomb_positions = generate_stage1_positions(WIDTH, HEIGHT)
stage1_adj = {node: adjacent_nodes_stage1(node, bomb_positions) for node in bomb_positions}
stage2_adj = {}
stage3_adj = {}


# ==========================================================
# Main Loop
# ==========================================================
while True:

    dt = clock.tick(FPS) / 1000.0
    state["dt"] = dt

    # ------------------------------------------------------
    # 이벤트 처리
    # ------------------------------------------------------
    for e in pygame.event.get():

        if state["state"] == "end_screen":
            if e.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(e.pos):
                pygame.quit()
                sys.exit()

        result = handle_events(
            e, state, stage, bomb_positions,
            start_rect, resume_btn, menu_btn, quit_btn,
            source1, source2, source3, stage1_adj,
            stage2_adj, stage3_adj
        )



        if result == "quit":
            pygame.quit()
            sys.exit()

        if result == "start_game":
            stage = 1
            state = init_game_state()

            state["state"] = "stage_start"
            state["stage_start_timer"] = 2.0
            state["stage_start_image"] = assets["stage1_start"]

            bomb_positions = generate_stage1_positions(WIDTH, HEIGHT)
            stage1_adj = {
                node: adjacent_nodes_stage1(node, bomb_positions)
                for node in bomb_positions
            }
            background_img = assets["stage1_bg"]

        if result == "menu":
            state = init_game_state()
            state["state"] = "menu"
            continue


    # ------------------------------------------------------
    # 메뉴 화면
    # ------------------------------------------------------
    if state["state"] == "menu":
        render_menu(screen, menu_img, start_img, start_rect)
        pygame.display.flip()
        continue


    # ------------------------------------------------------
    # Stage 시작 화면
    # ------------------------------------------------------
    if state["state"] == "stage_start":

        state["stage_start_timer"] -= dt
        screen.blit(state["stage_start_image"], (0, 0))
        pygame.display.flip()

        if state["stage_start_timer"] <= 0:
            state["explosion_timer"] = 0
            state["success_timer"] = 0

            state["state"] = "game"

            if stage == 1:
                start_new_round_stage1(state, bomb_positions, stage1_adj, source1)
            elif stage == 2:
                start_new_round_stage2(state, bomb_positions, stage2_adj, source2)
            elif stage == 3:
                start_new_round_stage3(state, bomb_positions, stage3_adj, source3)

        continue


    # ------------------------------------------------------
    # Stage3 결과 화면
    # ------------------------------------------------------
    if state["state"] == "stage_result":

        state["stage_start_timer"] -= dt
        screen.blit(state["stage_start_image"], (0, 0))
        pygame.display.flip()

        if state["stage_start_timer"] <= 0:
            state["state"] = "end_screen"

        continue


    # ------------------------------------------------------
    # Pause 화면
    # ------------------------------------------------------
    if state["state"] == "pause":
        render_pause(
            screen, background_img, WIDTH, HEIGHT, pause_font,
            resume_btn, menu_btn, quit_btn
        )
        pygame.display.flip()
        continue


    # ------------------------------------------------------
    # 결과 화면
    # ------------------------------------------------------
    if state["state"] == "end_screen":
        screen.blit(state["end_image"], (0, 0))
        screen.blit(exit_img, exit_rect)
        pygame.display.flip()
        continue


    # ======================================================
    # Stage3 종료 → 결과 판단
    # ======================================================
    if stage == 3 and state["round_count"] >= state["MAX_ROUNDS"]:

        if not state.get("game_finished"):

            total = state["success_count"] + state["fail_count"]
            rate = (state["success_count"] / total) if total > 0 else 0

            state["end_image"] = (
                assets["game_clear"] if rate >= 0.8 else assets["game_over"]
            )

            state["game_finished"] = True

            state["state"] = "stage_result"
            state["stage_start_timer"] = 2.0
            state["stage_start_image"] = state["end_image"]

        continue


    # ======================================================
    # Stage 전환 처리 (Stage1→2, Stage2→3)
    # ======================================================
    if stage in (1, 2) and state["waiting_stage_change"]:

        state["stage_transition_timer"] -= dt

        if state["stage_transition_timer"] <= 0:

            state["waiting_stage_change"] = False

            # Stage1 → 2
            if stage == 1:

                stage = 2
                bomb_positions = generate_stage2_positions()

                from logic.stage2_logic import build_stage2_adj
                stage2_adj = build_stage2_adj(bomb_positions)

                background_img = assets["stage2_bg"]
                state["round_count"] = 0

                state["state"] = "stage_start"
                state["stage_start_timer"] = 2.0
                state["stage_start_image"] = assets["stage2_start"]

                state["explosion_timer"] = 0
                state["success_timer"] = 0

            # Stage2 → 3
            else:

                stage = 3
                bomb_positions = generate_stage3_positions(WIDTH, HEIGHT)

                from logic.stage3_logic import build_stage3_adj
                stage3_adj = build_stage3_adj(bomb_positions)

                background_img = assets["stage3_bg"]
                state["round_count"] = 0

                state["state"] = "stage_start"
                state["stage_start_timer"] = 2.0
                state["stage_start_image"] = assets["stage3_start"]

                state["explosion_timer"] = 0
                state["success_timer"] = 0


        continue


    # ------------------------------------------------------
    # Pulse FSM
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


    # ======================================================
    # 게임 화면 렌더링
    # ======================================================
    if stage == 1:
        render_game(
            screen,
            background_img,
            stage,
            bomb_positions,
            black_bomb,
            red_bomb,
            exp_img,
            success_img,
            small_font,
            WIDTH,
            HEIGHT,
            state,
            stage1_adj,          # adj
            None,                # neighbor_func 없음
            (2, 2)               # center
        )

    elif stage == 2:
        render_game(
            screen,
            background_img,
            stage,
            bomb_positions,
            black_bomb,
            red_bomb,
            exp_img,
            success_img,
            small_font,
            WIDTH,
            HEIGHT,
            state,
            stage2_adj,          # adj
            adjacent_nodes_stage2,  # neighbor_func
            (2, 2)               # center
        )

    elif stage == 3:
        render_game(
            screen,
            background_img,
            stage,
            bomb_positions,
            black_bomb,
            red_bomb,
            exp_img,
            success_img,
            small_font,
            WIDTH,
            HEIGHT,
            state,
            stage3_adj,           # adj
            adjacent_nodes_stage3, # neighbor_func
            (2, 2)                # center
        )


    pygame.display.flip()

    # ------------------------------------------------------
    # Stage 전환 대기
    # ------------------------------------------------------
    if state.get("pending_stage_change"):

        # Stage3은 다음 스테이지가 없으므로 → 결과 화면으로 바로 이동
        if stage == 3:
            if state["explosion_timer"] <= 0 and state["success_timer"] <= 0:
                state["pending_stage_change"] = False
                state["state"] = "stage_result"
                state["stage_start_timer"] = 2.0
                state["stage_start_image"] = state["end_image"]
            continue

        # Stage1,2 → 정상적으로 다음 스테이지 이동
        if state["explosion_timer"] <= 0 and state["success_timer"] <= 0:
            state["pending_stage_change"] = False
            state["waiting_stage_change"] = True
            state["stage_transition_timer"] = 2.0