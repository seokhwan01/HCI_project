# ==========================================================
# logic/stage3_logic.py — Stage1 6-way Hex Version
# ==========================================================
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage3 import adjacent_nodes_stage3
from log_writer import write_log, utc_now
from settings import BOMB_RADIUS, BOMB_DISTANCE
W = BOMB_RADIUS * 2
A = BOMB_DISTANCE

# ----------------------------------------------------------
# Stage3 adjacency dict 생성 (6방향 hex)
# ----------------------------------------------------------
def build_stage3_adj(bomb_positions):
    adj = {}
    for node in bomb_positions:
        adj[node] = list(adjacent_nodes_stage3(node, bomb_positions))
    return adj


# ----------------------------------------------------------
# 중심/타깃 업데이트 (연결 6개일 때만 정상 중심)
# ----------------------------------------------------------
def update_next_nodes_stage3(state, bomb_positions, stage3_adj, exploded_node, source3):

    linked = list(adjacent_nodes_stage3(exploded_node, bomb_positions))
    print(f"   📎 중심 후보 {exploded_node} 연결 {len(linked)}개 → {linked}")

    # ★ 정상 중심 조건 = 연결 6개
    if len(linked) == 6:
        print(f"   ✅ 중심 후보 {exploded_node} → 중심 확정")
        state["current_source"] = exploded_node

        cand = get_candidates(exploded_node, 3, bomb_positions, stage3_adj)
        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 3, bomb_positions, stage3_adj, cand)
        else:
            print("   ⚠ 타깃 없음 → 자기 자신 설정")
            state["target_node"] = exploded_node

        state["connected_targets"] = linked
        print(f"   🎯 타깃 = {state['target_node']}")
        return

    # -----------------------------
    # 연결 부족 → 강제 (2,2) 리셋
    # -----------------------------
    print(f"   ❌ 연결 부족 → 중심을 {source3} 으로 리셋")

    reset_center = source3
    linked = list(adjacent_nodes_stage3(reset_center, bomb_positions))

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 3, bomb_positions, stage3_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 3, bomb_positions, stage3_adj, cand)
    else:
        print("   ⚠ 리셋 중심에서도 타깃 없음 → 자기 자신")
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")
    return



# ----------------------------------------------------------
# Stage3 새 라운드
# ----------------------------------------------------------
def start_new_round_stage3(state, bomb_positions, stage3_adj, source3):

    print_round_header("새 라운드 시작 (Stage 3)")

    state["mouse_locked_inside"] = True   # 🔒 라운드 시작 즉시 잠금
    state["red_start_time"] = None
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False
    state["explode_time"] = None
    state["click_time"] = None
    state["logged_after_explosion"] = False



    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0

    state["current_source"] = source3
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    cand = get_candidates(source3, 3, bomb_positions, stage3_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            source3, 3, bomb_positions, stage3_adj, cand)
    else:
        state["target_node"] = source3

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage3 폭발
# ----------------------------------------------------------
def explode_stage3(state, node, bomb_positions, stage3_adj, source3):

    # 🔥 현재 라운드 번호 백업 (late-click 용)
    state["trial_at_explosion"] = state["round_count"]

    # 🔥 폭발 시간 기록
    state["explode_time"] = utc_now()

    print_round_header("EXPLODE 처리 (Stage 3)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    state["mouse_locked_inside"] = False

    # 중심/타깃 갱신
    update_next_nodes_stage3(state, bomb_positions, stage3_adj, node, source3)

    if state["target_node"] is None:
        state["target_node"] = state["current_source"]

    # 라운드 증가
    state["fail_count"] += 1
    state["round_count"] += 1

    # ⭐⭐⭐ 반드시 초기화해야 late-click이 기록됨!
    state["click_time"] = None
    state["cursor_out_recorded"] = False
    state["logged_after_explosion"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 종료 조건
    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 종료 준비...")
        state["pending_stage_change"] = True
        return

    # 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0


# ----------------------------------------------------------
# Stage3 성공
# ----------------------------------------------------------
def handle_defuse_success_stage3(state, bomb_positions, stage3_adj, node, source3):
    state["click_time"] = utc_now()

    # 여기서 로그 한 줄 기록
    write_log(
        state["log_file"],
        N=6,                          # Stage1 → 연결 3개
        trial=state["round_count"],   # 현재 라운드
        W=W,
        A=A,                
        red_start_time=state.get("red_start_time",""),
        cursor_out_time=state.get("cursor_out_time",""),
        explode_time="",              # 성공했으므로 없음
        click_time=state["click_time"],
        success=1
    )

    print_round_header("DEFUSE SUCCESS (Stage 3)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["success_timer"] = 0.6
    state["success_pos"] = bomb_positions[node]

    state["mouse_locked_inside"] = False

    update_next_nodes_stage3(state, bomb_positions, stage3_adj, node, source3)

    if state["target_node"] is None:
        state["target_node"] = state["current_source"]

    state["round_count"] += 1
    state["success_count"] += 1

    #로그 초기화
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 종료 준비...")
        state["pending_stage_change"] = True
        return

    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
