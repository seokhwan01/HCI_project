# ==========================================================
# main.py — FINAL CLEAN VERSION (Stage Start + Transition + End Screens)
# ==========================================================
import math
import pygame, sys
from settings import WIDTH, HEIGHT, FPS, small_font, pause_font,BOMB_RADIUS
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

from log_writer import write_log, utc_now,init_log_file,generate_log_filename
from settings import BOMB_RADIUS, BOMB_DISTANCE
W = BOMB_RADIUS * 2
A = BOMB_DISTANCE


# ==========================================================
# Pygame 초기화
# ==========================================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("💣 폭탄 제거반 EOD")

STAGE_N = {
    1: 3,   # Stage 1 = hex → 연결 3개
    2: 4,   # Stage 2 = 십자 → 연결 4개
    3: 6    # Stage 3 = 원형 → 연결 6개
}

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

            # 🔥 게임 전용 로그 파일 생성
            state["log_file"] = generate_log_filename()
            init_log_file(state["log_file"])

        if result == "menu":
            state = init_game_state()
            state["state"] = "menu"
            continue

        # --------------------------------------------
        # 🔥🔥 폭발 후 이펙트 중 late-click 기록
        # --------------------------------------------
        if state.get("explosion_timer", 0) > 0:
            if e.type == pygame.MOUSEBUTTONDOWN:

                # 폭탄 중심
                x, y = bomb_positions[state["current_source"]]

                # 폭탄 있던 자리 hitbox 클릭인지 체크
                if (x - BOMB_RADIUS <= e.pos[0] <= x + BOMB_RADIUS) and \
                (y - BOMB_RADIUS <= e.pos[1] <= y + BOMB_RADIUS):

                    # 클릭 기록 (중복 방지)
                    if state.get("click_time") in (None, ""):
                        state["click_time"] = utc_now()


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
        # 🔒 펄스 시작 → 마우스 잠금 ON
        state["mouse_locked_inside"] = True
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
        # 🔥 여기에 red_start_time 기록
        state["red_start_time"] = utc_now()
        state["mouse_locked_inside"] = False   # 🔒

    # ======================================================
    # Mouse Clamp (폭탄 중심에 마우스 가두기)
    # ======================================================
    if state.get("mouse_locked_inside"):
        cx, cy = bomb_positions[state["current_source"]]   # 중심 폭탄 위치
        mx, my = pygame.mouse.get_pos()

        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)

        # BOMB_RADIUS 기반으로 clamp 반경 계산
        lock_radius =  BOMB_RADIUS * 0.6 #프레임으로 조금 더 밖으로 나가져서 offset 

        if dist > lock_radius:
            # 경계선으로 clamp
            scale = lock_radius / max(dist, 0.001)  
            new_x = cx + dx * scale
            new_y = cy + dy * scale

            # 마우스 위치 강제 이동
            pygame.mouse.set_pos((new_x, new_y))

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

    # ======================================================
    # 🔥 cursor_out_time 기록 (마우스 락 풀린 후)
    # ======================================================
    if state["fuse_burning"]:
        # 한 번만 기록되도록
        if state.get("cursor_out_time") is None:

            cx, cy = bomb_positions[state["current_source"]]
            mx, my = pygame.mouse.get_pos()

            dx = mx - cx
            dy = my - cy
            dist = math.hypot(dx, dy)

            # 폭탄 반경 밖으로 처음 나간 순간
            if dist > BOMB_RADIUS:
                state["cursor_out_time"] = utc_now()
                # print("cursor_out_time 기록됨:", state["cursor_out_time"])

                state["cursor_out_recorded"] = True
                print("커서가 밖에 나감 확인")
    # ======================================================
    # 🔥 폭발 후 이펙트 끝 → 이제 기록해도 되는 시점
    # ======================================================
    if state.get("explode_time") and not state.get("logged_after_explosion"):

        # explosion effect 끝났는지 확인
        if state.get("explosion_timer", 0) <= 0:
            N_value = STAGE_N.get(stage, 3)   # stage 1→3 등 자동 매핑
            trial_value = state.get("trial_at_explosion", state["round_count"])
            write_log(
                state["log_file"],
                N=N_value,
                trial=trial_value,
                W=W,
                A=A,
                red_start_time=state.get("red_start_time",""),
                cursor_out_time=state.get("cursor_out_time",""),
                explode_time=state.get("explode_time",""),
                click_time=state.get("click_time",""),
                success=0
            )

            # 🔥 이번 폭발에 대한 실패 로그는 찍었으니까
            # 다음 라운드를 위해 값들 리셋
            state["logged_after_explosion"] = True
            state["cursor_out_time"] = None       # ★ 이 줄이 핵심
            state["cursor_out_recorded"] = False
            state["explode_time"] = None          # 다음 폭발 구분용(선택)

    # ======================================================
    # Stage3 종료 → 결과 판단 (이펙트 끝날 때까지 대기)
    # ======================================================
    if stage == 3 and state["round_count"] >= state["MAX_ROUNDS"]:

        # ① 아직 결과 계산 안 했으면 → 지금 계산만 하고 끝
        if not state.get("game_finished"):

            total = state["success_count"] + state["fail_count"]
            rate = (state["success_count"] / total) if total > 0 else 0

            state["end_image"] = (
                assets["game_clear"] if rate >= 0.8 else assets["game_over"]
            )

            state["game_finished"] = True

            # 이펙트가 끝날 때까지 기다림
            continue

        # ② 이펙트 남아있으면 계속 기다림
        if state["explosion_timer"] > 0 or state["success_timer"] > 0:
            continue

        # ③ 이제 결과 화면으로 이동
        state["pending_stage_change"] = False
        state["state"] = "stage_result"
        state["stage_start_timer"] = 2.0
        state["stage_start_image"] = state["end_image"]

        continue



    # ------------------------------------------------------
    # Stage 전환 대기 (Stage1→2, Stage2→3)
    # ------------------------------------------------------
    if state.get("pending_stage_change"):

        # Stage3은 아래에서 처리했으므로 실행되면 안 됨
        if stage == 3:
            continue

        # Stage1,2 → 다음 스테이지 이동
        if state["explosion_timer"] <= 0 and state["success_timer"] <= 0:
            state["pending_stage_change"] = False
            state["waiting_stage_change"] = True
            state["stage_transition_timer"] = 2.0
