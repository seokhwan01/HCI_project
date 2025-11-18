# ==========================================================
# logic/stage2_logic.py — ROUND 표시 강화 버전
# ==========================================================
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage2 import adjacent_nodes_stage2
from log_writer import write_log, utc_now
from settings import BOMB_RADIUS, BOMB_DISTANCE
W = BOMB_RADIUS * 2
A = BOMB_DISTANCE

# ----------------------------------------------------------
# Stage2 adjacency dict 생성 (십자 구조 기반)
# ----------------------------------------------------------
def build_stage2_adj(bomb_positions):
    adj = {}
    for node in bomb_positions:
        adj[node] = list(adjacent_nodes_stage2(node, bomb_positions))
    return adj


# ----------------------------------------------------------
# Stage2 중심/타깃 업데이트
# ----------------------------------------------------------
def update_next_nodes_stage2(state, bomb_positions, stage2_adj, exploded_node, source2):

    linked = stage2_adj.get(exploded_node, [])
    print(f"   📎 연결된 폭탄: {linked}")

    # ⭐ Stage2는 연결 4개여야 정상 중심
    if len(linked) == 4:
        print(f"   ✅ 중심 후보 {exploded_node} 연결 4개 → 중심 확정")

        state["current_source"] = exploded_node
        state["connected_targets"] = linked

        cand = get_candidates(exploded_node, 2, bomb_positions, stage2_adj)
        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 2, bomb_positions, stage2_adj, cand)
        else:
            state["target_node"] = exploded_node

        print(f"   🎯 다음 타깃 = {state['target_node']}")
        return

    # ❌ 연결 4개가 아니면 → 기본 중심(source2)으로 리셋
    print(f"   ❌ 연결 부족 → 중심을 {source2} 으로 리셋")

    reset_center = source2
    linked = stage2_adj.get(reset_center, [])

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 2, bomb_positions, stage2_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 2, bomb_positions, stage2_adj, cand)
    else:
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage2 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage2(state, bomb_positions, stage2_adj, source2):

    round_num = state["round_count"]
    print_round_header(f"🔵 ROUND {round_num} 시작 (Stage 2)")

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

    state["current_source"] = source2
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    cand = get_candidates(source2, 2, bomb_positions, stage2_adj)
    state["target_node"] = choose_next_target_common(
        source2, 2, bomb_positions, stage2_adj, cand)

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


def explode_stage2(state, node, bomb_positions, stage2_adj, source2):

    # 현재 라운드 번호 백업 (late-click용)
    state["trial_at_explosion"] = state["round_count"]

    # 폭발 시간 기록
    state["explode_time"] = utc_now()

    print_round_header(f"EXPLODE 처리 (Stage 2)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    state["mouse_locked_inside"] = False

    # 중심/타깃 갱신
    update_next_nodes_stage2(state, bomb_positions, stage2_adj, node, source2)

    # 라운드 증가
    state["fail_count"] += 1
    state["round_count"] += 1

    # ⭐⭐⭐ 반드시 초기화해야 late-click 기록됨
    state["click_time"] = None
    state["cursor_out_recorded"] = False
    state["logged_after_explosion"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 종료 조건
    if state["round_count"] >= state["MAX_ROUNDS"]:
        state["pending_stage_change"] = True
        return

    # 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0


# ----------------------------------------------------------
# Stage2 성공 처리
# ----------------------------------------------------------
def handle_defuse_success_stage2(state, bomb_positions, stage2_adj, node, source2):
    # 클릭 성공 시점 기록
    state["click_time"] = utc_now()

    # 여기서 로그 한 줄 기록
    write_log(
        state["log_file"],
        N=4,                          # Stage1 → 연결 3개
        trial=state["round_count"],   # 현재 라운드
        W=W,
        A=A,                
        red_start_time=state.get("red_start_time",""),
        cursor_out_time=state.get("cursor_out_time",""),
        explode_time="",              # 성공했으므로 없음
        click_time=state["click_time"],
        success=1
    )

    round_num = state["round_count"]
    print_round_header(f"🟢 ROUND {round_num} – 성공 (Stage 2)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["success_timer"] = 0.6
    state["success_pos"] = bomb_positions[node]

    state["success_count"] += 1
    state["round_count"] += 1

    #로그 초기화
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    state["mouse_locked_inside"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # Stage3 전환
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
