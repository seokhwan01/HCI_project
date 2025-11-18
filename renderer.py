import pygame
import math
from fuse import draw_fuse
from particles import update_particles
from settings import FUSE_SPEED, PULSE_SPEED
from logic.stage1_logic import explode_stage1
from logic.stage2_logic import explode_stage2
from logic.stage3_logic import explode_stage3

_last_render_source = None
_printed_fuse_distances = set()
_last_logged_round = None


# ==========================================================
# 메뉴
# ==========================================================
def render_menu(screen, menu_img, start_img, start_rect):
    screen.blit(menu_img, (0, 0))
    screen.blit(start_img, start_rect)
    pygame.display.flip()


# ==========================================================
# 일시정지
# ==========================================================
def render_pause(screen, background_img, WIDTH, HEIGHT, pause_font,
                 resume_btn, menu_btn, quit_btn):

    screen.blit(background_img, (0, 0))

    dark = pygame.Surface((WIDTH, HEIGHT))
    dark.set_alpha(180)
    dark.fill((0, 0, 0))
    screen.blit(dark, (0, 0))

    title = pause_font.render("일시정지", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 160))

    pygame.draw.rect(screen, (230, 230, 230), resume_btn, border_radius=20)
    pygame.draw.rect(screen, (200, 200, 100), menu_btn, border_radius=20)
    pygame.draw.rect(screen, (200, 100, 100), quit_btn, border_radius=20)

    screen.blit(pause_font.render("계속하기", True, (0, 0, 0)),
                (resume_btn.centerx - 100, resume_btn.centery - 25))
    screen.blit(pause_font.render("메인메뉴", True, (0, 0, 0)),
                (menu_btn.centerx - 100, menu_btn.centery - 25))
    screen.blit(pause_font.render("종료하기", True, (0, 0, 0)),
                (quit_btn.centerx - 100, quit_btn.centery - 25))

    pygame.display.flip()


# ==========================================================
# ★ 게임 플레이 화면 렌더링 (완전히 정리된 버전)
# ==========================================================
def render_game(screen, background_img, stage, bomb_positions,
                black_bomb, red_bomb, exp_img, success_img, small_font,
                WIDTH, HEIGHT, state,
                adj,               # ← 현재 스테이지 adjacency dict
                neighbor_func,     # ← Stage2 adjacency 함수 / Stage1·3 = None
                center_node):      # ← (2,2)

    global _last_render_source, _printed_fuse_distances, _last_logged_round

    dt = state.get("dt", 0.016)

    # ---------------------------
    # 라운드 변경 → 거리 로그 초기화
    # ---------------------------
    current_round = state["round_count"]
    if current_round != _last_logged_round:
        _printed_fuse_distances.clear()
        _last_logged_round = current_round

    screen.blit(background_img, (0, 0))

    # ---------------------------
    # 1) 중심 기준 도화선 렌더링
    # ---------------------------
    current = state["current_source"]

    if current in bomb_positions:

        # 🔥 stage2뿐 아니라 stage3도 neighbor_func 사용
        if neighbor_func is not None:
            connected_nodes = list(neighbor_func(current, bomb_positions))
        else:
            connected_nodes = adj.get(current, [])


        drawn = []

        for nb in connected_nodes:
            if nb in bomb_positions:
                draw_fuse(screen, bomb_positions[current], bomb_positions[nb])
                drawn.append(str(nb))

                ax, ay = bomb_positions[current]
                bx, by = bomb_positions[nb]
                dist = math.dist((ax, ay), (bx, by))

                key = (current, nb)
                if key not in _printed_fuse_distances:
                    print(f"📏 도화선 거리: {current} → {nb} = {dist:.2f}px")
                    _printed_fuse_distances.add(key)

        if drawn and current != _last_render_source:
            print(f"🎨 [렌더] 도화선: {current} → {', '.join(drawn)}")
            _last_render_source = current

    # ---------------------------
    # 2) Pulse 애니메이션
    # ---------------------------
    if state["pulsing"]:
        p = state["pulse_target"]
        if p in bomb_positions:
            state["pulse_timer"] += dt * PULSE_SPEED
            px, py = bomb_positions[p]
            scale = 1 + 0.4 * math.sin(state["pulse_timer"])
            img = pygame.transform.scale(black_bomb, (int(60 * scale), int(60 * scale)))
            screen.blit(img, img.get_rect(center=(px, py)))

    # ---------------------------
    # 3) Fuse Burning → 폭발
    # ---------------------------
    if state["fuse_burning"] and state["target_node"] in bomb_positions:

        src = bomb_positions[state["current_source"]]
        dst = bomb_positions[state["target_node"]]

        draw_fuse(screen, src, dst, progress=state["segment_progress"], active=True)
        state["segment_progress"] += dt * (FUSE_SPEED * 0.15)

        if state["segment_progress"] >= 1:

            node = state["target_node"]

            if stage == 1:
                explode_stage1(state, node, bomb_positions, adj, center_node)

            elif stage == 2:
                explode_stage2(state, node, bomb_positions, adj, center_node)

            else:
                explode_stage3(state, node, bomb_positions, adj, center_node)

    # ---------------------------
    # 4) 폭탄 렌더링
    # ---------------------------
    for node, pos in bomb_positions.items():

        # 🔥 stage2뿐 아니라 stage3도 neighbor_func 사용
        if neighbor_func is not None:
            active = [state["current_source"]] + list(neighbor_func(state["current_source"], bomb_positions))
        else:
            active = [state["current_source"]] + adj.get(state["current_source"], [])


        dim = node not in active
        burning = state["fuse_burning"] and node == state["target_node"]

        img = red_bomb if burning else black_bomb
        img.set_alpha(100 if dim else 255)
        screen.blit(img, img.get_rect(center=pos))

    # ---------------------------
    # 5) 폭발 이미지
    # ---------------------------
    if state["explosion_timer"] > 0:
        screen.blit(exp_img, exp_img.get_rect(center=state["explosion_pos"]))
        state["explosion_timer"] -= dt

    update_particles(screen)

    # ---------------------------
    # 6) 성공 효과
    # ---------------------------
    if state.get("success_timer", 0) > 0:
        screen.blit(success_img, success_img.get_rect(center=state["success_pos"]))
        state["success_timer"] -= dt

    # ---------------------------
    # 7) UI
    # ---------------------------
    info = small_font.render(
        f"[STAGE {stage} / ROUND {state['round_count']}]", True, (0, 0, 0)
    )
    success_text = small_font.render(f"성공 : {state['success_count']}", True, (0, 180, 0))
    fail_text = small_font.render(f"실패 : {state['fail_count']}", True, (200, 0, 0))
    msg = small_font.render(state["game_message"], True, (20, 20, 20))

    screen.blit(info, (20, 20))
    screen.blit(success_text, (20, 60))
    screen.blit(fail_text, (20, 95))
    screen.blit(msg, (20, 140))

    pygame.display.flip()
