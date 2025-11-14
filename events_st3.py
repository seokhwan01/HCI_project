import pygame
import math
from logic.stage1_logic import handle_defuse_success_stage1
from logic.stage2_logic import handle_defuse_success_stage2
from logic.stage3_logic import handle_defuse_success_stage3
from settings import MOUSE_LOCK_ON_START


def safe_collide(rect, pos):
    """rect가 None이면 False 반환"""
    return rect is not None and rect.collidepoint(pos)


def handle_events(e, state, stage, bomb_positions,
                  start_rect, resume_btn, menu_btn, quit_btn,
                  source1, source2, stage_adj):

    # -------------------------------
    # 🔚 프로그램 종료
    # -------------------------------
    if e.type == pygame.QUIT:
        return "quit"

    # -------------------------------
    # ⏸ ESC → 일시정지 토글
    # -------------------------------
    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
        if state["state"] == "game":
            state["state"] = "pause"
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        elif state["state"] == "pause":
            state["state"] = "game"
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(True)

    # -------------------------------
    # 🏠 MENU 상태
    # -------------------------------
    if state["state"] == "menu":
        if e.type == pygame.MOUSEBUTTONDOWN and safe_collide(start_rect, e.pos):
            state["state"] = "game"
            if MOUSE_LOCK_ON_START:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(True)
        return None

    # -------------------------------
    # ⏸ PAUSE 메뉴
    # -------------------------------
    if state["state"] == "pause":
        if e.type == pygame.MOUSEBUTTONDOWN:
            if safe_collide(resume_btn, e.pos):
                state["state"] = "game"
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(True)
            elif safe_collide(menu_btn, e.pos):
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                return "menu"
            elif safe_collide(quit_btn, e.pos):
                return "quit"
        return None

    # -------------------------------
    # 💣 GAME 상태 — 폭탄 클릭 판정
    # -------------------------------
    if state["state"] == "game" and e.type == pygame.MOUSEBUTTONDOWN:

        if not state["fuse_burning"] or not state["target_node"]:
            return None

        mx, my = e.pos
        tx, ty = bomb_positions[state["target_node"]]

        if math.hypot(mx - tx, my - ty) <= 35:
            # -----------------------
            # Stage별로 해제 처리
            # -----------------------
            if stage == 1:
                handle_defuse_success_stage1(state, bomb_positions, stage_adj, state["target_node"], source1)
            elif stage == 2:
                handle_defuse_success_stage2(state, bomb_positions, stage_adj, state["target_node"], source2)
            elif stage == 3:
                handle_defuse_success_stage3(state, bomb_positions, stage_adj, state["target_node"])
        else:
            state["game_message"] = "❌ 잘못된 폭탄 클릭!"

    return None
