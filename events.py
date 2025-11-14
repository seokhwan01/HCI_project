import pygame
import math
from logic.stage1_logic import handle_defuse_success_stage1
from logic.stage2_logic import handle_defuse_success_stage2
from logic.stage3_logic import handle_defuse_success_stage3
from settings import MOUSE_LOCK_ON_START


def safe_hit(rect, pos):
    """rect가 None일 때 collidepoint 호출 방지"""
    if rect is None:
        return False
    return rect.collidepoint(pos)


def handle_events(e, state, stage, bomb_positions,
                  start_rect, resume_btn, menu_btn, quit_btn,
                  source1, source2, stage1_adj):

    # -----------------------------------------
    # 🔚 창 종료
    # -----------------------------------------
    if e.type == pygame.QUIT:
        return "quit"

    # -----------------------------------------
    # ⏸ ESC → 일시정지 토글
    # -----------------------------------------
    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
        if state["state"] == "game":
            state["state"] = "pause"
            pygame.event.set_grab(False)      # 🔓 마우스 해제
            pygame.mouse.set_visible(True)

        elif state["state"] == "pause":
            state["state"] = "game"
            pygame.event.set_grab(True)       # 🔒 마우스 고정
            pygame.mouse.set_visible(True)

        return None

    # -----------------------------------------
    # 🏠 MENU 화면
    # -----------------------------------------
    if state["state"] == "menu":
        if e.type == pygame.MOUSEBUTTONDOWN and safe_hit(start_rect, e.pos):
            state["state"] = "game"

            if MOUSE_LOCK_ON_START:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(True)

            return "start_game"   # ★ ONLY 안쪽에서 반환
        return None


    # -----------------------------------------
    # ⏸ PAUSE 화면
    # -----------------------------------------
    if state["state"] == "pause":
        if e.type == pygame.MOUSEBUTTONDOWN:

            if safe_hit(resume_btn, e.pos):
                state["state"] = "game"
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(True)

            elif safe_hit(menu_btn, e.pos):
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                return "menu"

            elif safe_hit(quit_btn, e.pos):
                return "quit"

        return None

    # -----------------------------------------
    # 💣 GAME 상태 — 폭탄 클릭 처리
    # -----------------------------------------
    if state["state"] == "game" and e.type == pygame.MOUSEBUTTONDOWN:

        # 게임 중엔 항상 마우스를 고정 유지 ★
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)

        if state["fuse_burning"] and state["target_node"]:

            mx, my = e.pos
            tx, ty = bomb_positions[state["target_node"]]

            if math.hypot(mx - tx, my - ty) <= 35:

                if stage == 1:
                    handle_defuse_success_stage1(
                        state, bomb_positions, stage1_adj,
                        state["target_node"], source1
                    )

                elif stage == 2:
                    handle_defuse_success_stage2(
                        state, bomb_positions, stage1_adj,
                        state["target_node"], source2
                    )

                elif stage == 3:
                    handle_defuse_success_stage3(
                        state, bomb_positions, stage1_adj,  # stage3_adj는 render_game으로만 필요
                        state["target_node"]
                    )

            else:
                state["game_message"] = "❌ 잘못된 폭탄 클릭!"

    return None
