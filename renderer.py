import pygame
import math
from fuse import draw_fuse
from particles import update_particles
from settings import FUSE_SPEED, PULSE_SPEED
from logic.stage1_logic import explode_stage1
from logic.stage2_logic import explode_stage2
from logic.stage3_logic import explode_stage3   # ★ Stage3 전용 폭발 함수

# 🔹 렌더링 시 중심 폭탄이 변경됐는지 기록해 로그 중복 방지
_last_render_source = None


# ============================================================
#                    메인 메뉴 화면 렌더링
# ============================================================
def render_menu(screen, menu_img, start_img, start_rect):
    """
    메인 메뉴 첫 화면 출력.
    - 배경(menu_img) 출력
    - Start 버튼 출력
    """
    screen.blit(menu_img, (0, 0))
    screen.blit(start_img, start_rect)
    pygame.display.flip()


# ============================================================
#                    일시정지 화면 렌더링
# ============================================================
def render_pause(screen, background_img, WIDTH, HEIGHT, pause_font,
                 resume_btn, menu_btn, quit_btn):
    """
    - 이전 화면을 반투명 어둡게 덮는다.
    - 일시정지 UI 3종 버튼 출력
    """
    screen.blit(background_img, (0, 0))

    # 반투명 레이어
    dark = pygame.Surface((WIDTH, HEIGHT))
    dark.set_alpha(180)
    dark.fill((0, 0, 0))
    screen.blit(dark, (0, 0))

    # "일시정지" 텍스트
    title = pause_font.render("일시정지", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 160))

    # 버튼 3종 그리기
    pygame.draw.rect(screen, (230, 230, 230), resume_btn, border_radius=20)
    pygame.draw.rect(screen, (200, 200, 100), menu_btn, border_radius=20)
    pygame.draw.rect(screen, (200, 100, 100), quit_btn, border_radius=20)

    # 버튼 안의 텍스트
    screen.blit(pause_font.render("계속하기", True, (0, 0, 0)),
                (resume_btn.centerx - 100, resume_btn.centery - 25))
    screen.blit(pause_font.render("메인메뉴", True, (0, 0, 0)),
                (menu_btn.centerx - 100, menu_btn.centery - 25))
    screen.blit(pause_font.render("종료하기", True, (0, 0, 0)),
                (quit_btn.centerx - 100, quit_btn.centery - 25))

    pygame.display.flip()


# ============================================================
#         ★ 게임 플레이 화면 전체를 렌더링하는 핵심 함수 ★
# ============================================================
def render_game(screen, background_img, stage, bomb_positions,
                black_bomb, red_bomb, exp_img, small_font,
                WIDTH, HEIGHT, state,
                stage1_connections, stage1_adj,
                adjacent_nodes_stage2, stage3_adj):
    """
    화면 하나를 구성하는 모든 요소를 하나씩 그리는 메인 렌더링 함수.

    처리 순서:
      1) 배경 그리기
      2) 중심 폭탄과 연결된 도화선 전체 그리기
      3) 펄스 애니메이션 (흔들리는 효과)
      4) 도화선 이동(점화) 애니메이션
      5) 모든 폭탄 이미지 렌더링
      6) 폭발 이미지 / 파티클
      7) 텍스트 UI (STAGE / ROUND / 메시지)
    """

    global _last_render_source
    dt = state.get("dt", 0.016)  # delta-time (프레임 간 시간)

    # ======================================================
    # 0) 배경 출력
    # ======================================================
    screen.blit(background_img, (0, 0))

    # ======================================================
    # 1) 도화선(fuse) 연결 라인 렌더링
    # ======================================================
    current = state["current_source"]  # 현재 중심 폭탄

    if current and current in bomb_positions:

        # Stage에 따라 인접 노드 목록이 다름
        if stage == 1:
            connected_nodes = stage1_adj.get(current, [])
        elif stage == 2:
            connected_nodes = list(adjacent_nodes_stage2(current, bomb_positions))
        else:
            connected_nodes = stage3_adj.get(current, [])

        drawn_fuses = []

        # 중심 노드 → 연결된 모든 노드에 선(도화선) 그리기
        for nb in connected_nodes:
            if nb in bomb_positions:
                draw_fuse(screen, bomb_positions[current], bomb_positions[nb])
                drawn_fuses.append(str(nb))

        # 중심이 바뀌면 도화선 정보 로그 출력 (중복 출력 방지)
        if drawn_fuses and current != _last_render_source:
            print(f"🎨 [렌더] 도화선: {current} → {', '.join(drawn_fuses)}")
            _last_render_source = current

    # ======================================================
    # 2) Pulsing 애니메이션 (폭탄이 부풀었다 줄어드는 효과)
    # ======================================================
    if state["pulsing"]:
        pulse_target = state["pulse_target"]

        if pulse_target in bomb_positions:
            # sin 함수로 크기 변화 — 흔들리는 효과
            state["pulse_timer"] += dt * PULSE_SPEED
            px, py = bomb_positions[pulse_target]
            scale = 1 + 0.40 * math.sin(state["pulse_timer"])

            # 크기 변형된 이미지 다시 렌더링
            img = pygame.transform.scale(black_bomb, (int(60 * scale), int(60 * scale)))
            screen.blit(img, img.get_rect(center=(px, py)))

    # ======================================================
    # 3) 도화선 "타고가는" 애니메이션 (Fuse Burning)
    # ======================================================
    if state["fuse_burning"] and state["target_node"] in bomb_positions:

        # 시작점(중심) → 목표 노드까지
        a = bomb_positions[state["current_source"]]
        b = bomb_positions[state["target_node"]]

        # 진행률(progress)에 따라 도화선이 채워지는 방식
        draw_fuse(screen, a, b, progress=state["segment_progress"], active=True)

        # 진행률 증가
        state["segment_progress"] += dt * (FUSE_SPEED * 0.15)

        # 도화선 끝 도달 → 폭발 로직 호출
        if state["segment_progress"] >= 1:

            if stage == 1:
                explode_stage1(state, state["target_node"], bomb_positions, stage1_adj, (2, 3))

            elif stage == 2:
                explode_stage2(state, state["target_node"], bomb_positions, stage1_adj, (2, 2))

            else:
                explode_stage3(state, state["target_node"], bomb_positions, stage3_adj)

    # ======================================================
    # 4) 모든 폭탄 렌더링 (비활성/활성/점화 상태 포함)
    # ======================================================
    for node, pos in bomb_positions.items():

        # Stage별로 "활성(active)" 폭탄 판정 방식이 다름
        if stage == 1:
            active = [state["current_source"]] + stage1_adj.get(state["current_source"], [])
        elif stage == 2:
            active = [state["current_source"]] + list(adjacent_nodes_stage2(state["current_source"], bomb_positions))
        else:
            active = [state["current_source"]] + stage3_adj.get(state["current_source"], [])

        dim = node not in active  # 활성 폭탄이 아니면 dim 적용(투명하게)
        burning = state["fuse_burning"] and node == state["target_node"]  # 목표 노드는 빨간색

        img = red_bomb if burning else black_bomb
        img.set_alpha(100 if dim else 255)   # 비활성은 흐리게 렌더링
        screen.blit(img, img.get_rect(center=pos))

    # ======================================================
    # 5) 폭발 이펙트 + 파티클 처리
    # ======================================================
    if state["explosion_timer"] > 0:
        screen.blit(exp_img, exp_img.get_rect(center=state["explosion_pos"]))
        state["explosion_timer"] -= dt

    update_particles(screen)

    # ======================================================
    # 6) UI 텍스트 (Stage / Round / 메시지)
    # ======================================================
    info = small_font.render(
        f"[STAGE {stage} / ROUND {state['round_count']}]", True, (0, 0, 0)
    )
    msg = small_font.render(state["game_message"], True, (20, 20, 20))

    screen.blit(info, (20, 20))
    screen.blit(msg, (20, 60))

    pygame.display.flip()
