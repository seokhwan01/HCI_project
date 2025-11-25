# ==========================================================
# logic/stage2_logic.py — FINAL VERSION (Condition-aware)
# ==========================================================
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage2 import adjacent_nodes_stage2
from log_writer import write_log, utc_now
import settings   # 🔥 ALWAYS USE SETTINGS FOR W, A


# ----------------------------------------------------------
# 항상 최신 W, A 반환 (settings가 실험 조건마다 바뀜)
# ----------------------------------------------------------
def get_W():
    return settings.BOMB_RADIUS * 2

def get_A():
    return settings.BOMB_DISTANCE


# ----------------------------------------------------------
# Stage2 adjacency dict 생성
# ----------------------------------------------------------
def build_stage2_adj(bomb_positions):
    adj = {}
    for node in bomb_positions:
        adj[node] = list(adjacent_nodes_stage2(node, bomb_positions))
    return adj


# ----------------------------------------------------------
# Stage2 중심/타깃 업데이트 (십자형 → 연결 4개 필수)
# ----------------------------------------------------------
def update_next_nodes_stage2(state, bomb_positions, stage2_adj, exploded_node, source2):

    linked = stage2_adj.get(exploded_node, [])
    print(f"   📎 중심 후보 {exploded_node} 연결 수 = {len(linked)} → {linked}")

    if len(linked) == 4:
        print(f"   ✅ 중심 후보 {exploded_node} 정상 (4개) → 중심 확정")

        state["current_source"] = exploded_node
        state["connected_targets"] = linked

        cand = get_candidates(exploded_node, 2, bomb_positions, stage2_adj)
        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 2, bomb_positions, stage2_adj, cand
            )
        else:
            state["target_node"] = exploded_node

        print(f"   🎯 타깃 = {state['target_node']}")
        return

    # ------------------------------------------------------
    # 연결 4개 아니면 무조건 중심 리셋
    # ------------------------------------------------------
    print(f"   ❌ 연결 부족 → 중심을 {source2} 로 리셋")

    reset_center = source2
    linked = stage2_adj.get(reset_center, [])

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 2, bomb_positions, stage2_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 2, bomb_positions, stage2_adj, cand
        )
    else:
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage2 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage2(state, bomb_positions, stage2_adj, source2):

    print_round_header("새 라운드 시작 (Stage 2)")

    # 초기화
    state["mouse_locked_inside"] = True
    state["red_start_time"] = None
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False
    state["explode_time"] = None
    state["click_time"] = None
    state["logged_after_explosion"] = False

    # 펄스 초기화
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0

    # 중심
    state["current_source"] = source2
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    # 타깃 선택
    cand = get_candidates(source2, 2, bomb_positions, stage2_adj)
    state["target_node"] = choose_next_target_common(
        source2, 2, bomb_positions, stage2_adj, cand
    )

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage2 폭발 처리
# ----------------------------------------------------------
def explode_stage2(state, node, bomb_positions, stage2_adj, source2):

    state["trial_at_explosion"] = state["round_count"]
    state["explode_time"] = utc_now()

    print_round_header("EXPLODE 처리 (Stage 2)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]
    state["mouse_locked_inside"] = False

    update_next_nodes_stage2(state, bomb_positions, stage2_adj, node, source2)

    # 라운드 증가
    state["fail_count"] += 1
    state["round_count"] += 1

    # 초기화
    state["click_time"] = None
    state["cursor_out_recorded"] = False
    state["logged_after_explosion"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 전환 검사
    if state["round_count"] >= state["MAX_ROUNDS"]:
        state["pending_stage_change"] = True
        return

    # 다음 pulse 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0


# ----------------------------------------------------------
# Stage2 성공 처리
# ----------------------------------------------------------
def handle_defuse_success_stage2(state, bomb_positions, stage2_adj, node, source2):

    state["click_time"] = utc_now()

    # 🔥 로깅 — 최신 조건값 적용(get_W/get_A)
    write_log(
        state["log_file"],
        N=4,                          # Stage2 = 연결 4개
        trial=state["round_count"],
        W=get_W(),
        A=get_A(),
        red_start_time=state.get("red_start_time", ""),
        cursor_out_time=state.get("cursor_out_time", ""),
        explode_time="",              # 성공 → 폭발 없음
        click_time=state["click_time"],
        success=1
    )

    print_round_header("DEFUSE SUCCESS (Stage 2)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["success_timer"] = 0.6
    state["success_pos"] = bomb_positions[node]
    state["mouse_locked_inside"] = False

    # 라운드 증가
    state["success_count"] += 1
    state["round_count"] += 1

    # 초기화
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 전환 검사
    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 3 전환 준비...")
        state["pending_stage_change"] = True
        return

    # 중심/타깃 갱신
    update_next_nodes_stage2(state, bomb_positions, stage2_adj, node, source2)

    # 다음 pulse
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
