# logic/stage1_logic.py
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage1 import adjacent_nodes_stage1
from log_writer import write_log, utc_now
import settings   # settings.BOMB_RADIUS / BOMB_DISTANCE 최신값 사용


# ----------------------------------------------------------
# 항상 최신 W, A 값 반환 (조건 변경마다 자동 반영)
# ----------------------------------------------------------
def get_W():
    return settings.BOMB_RADIUS * 2

def get_A():
    return settings.BOMB_DISTANCE


# ----------------------------------------------------------
# Stage1 중심/타깃 업데이트
# ----------------------------------------------------------
def update_next_nodes_stage1(state, bomb_positions, stage1_adj, exploded_node, source1):

    linked = list(adjacent_nodes_stage1(exploded_node, bomb_positions))
    print(f"   📎 중심 후보 {exploded_node} 연결 수: {len(linked)} → {linked}")

    # 정상 중심(3개 연결)
    if len(linked) == 3:
        print(f"   ✅ 중심 후보 {exploded_node} 연결 3개 → 중심 확정")

        state["current_source"] = exploded_node
        cand = get_candidates(exploded_node, 1, bomb_positions, stage1_adj)

        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 1, bomb_positions, stage1_adj, cand
            )
        else:
            print("   ⚠ 타깃 후보 없음 → 자기 자신")
            state["target_node"] = exploded_node

        state["connected_targets"] = linked
        print(f"   🎯 타깃 = {state['target_node']}")
        return

    # ------------------------------------------------------------------
    # 3개가 아닐 경우 → 무조건 중심을 (2,2) 로 리셋
    # ------------------------------------------------------------------
    print("   ❌ 중심 후보 연결 부족 → 중심을 (2,2)으로 리셋")

    reset_center = source1
    linked = list(adjacent_nodes_stage1(reset_center, bomb_positions))

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 1, bomb_positions, stage1_adj)

    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 1, bomb_positions, stage1_adj, cand
        )
    else:
        print("   ⚠ 리셋 중심에서도 타깃 없음 → 자기 자신")
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage1 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage1(state, bomb_positions, stage1_adj, source1):

    print_round_header("새 라운드 시작 (Stage 1)")

    state["mouse_locked_inside"] = True   # 🔒 처음부터 잠금
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

    # 중심 = (2,2)
    state["current_source"] = source1
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    cand = get_candidates(source1, 1, bomb_positions, stage1_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            source1, 1, bomb_positions, stage1_adj, cand
        )
    else:
        print("⚠ 시작 라운드 타깃 없음 → 자기 자신")
        state["target_node"] = source1

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# 폭발 처리
# ----------------------------------------------------------
def explode_stage1(state, node, bomb_positions, stage1_adj, source1):

    state["trial_at_explosion"] = state["round_count"]
    state["explode_time"] = utc_now()

    print_round_header("EXPLODE 처리 (Stage 1)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]
    state["mouse_locked_inside"] = False

    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    if state["target_node"] is None:
        state["target_node"] = state["current_source"]

    # 라운드 증가
    state["fail_count"] += 1
    state["round_count"] += 1

    state["click_time"] = None
    state["cursor_out_recorded"] = False
    state["logged_after_explosion"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    if state["round_count"] >= state["MAX_ROUNDS"]:
        state["pending_stage_change"] = True
        return

    # 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0



# ----------------------------------------------------------
# Stage1 성공 처리
# ----------------------------------------------------------
def handle_defuse_success_stage1(state, bomb_positions, stage1_adj, node, source1):

    state["click_time"] = utc_now()

    # 🔥 항상 최신 조건값 get_W(), get_A() 사용
    write_log(
        state["log_file"],
        N=3,
        trial=state["round_count"],
        W=get_W(),
        A=get_A(),
        red_start_time=state.get("red_start_time", ""),
        cursor_out_time=state.get("cursor_out_time", ""),
        explode_time="",
        click_time=state["click_time"],
        success=1
    )

    print_round_header("DEFUSE SUCCESS (Stage 1)", node)

    # 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["success_timer"] = 0.6
    state["success_pos"] = bomb_positions[node]
    state["mouse_locked_inside"] = False

    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    if state["target_node"] is None:
        state["target_node"] = state["current_source"]

    # 라운드 증가
    state["round_count"] += 1
    state["success_count"] += 1

    # 초기화
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # Stage1 → Stage2 전환
    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 2 전환 준비...")
        state["pending_stage_change"] = True
        return

    # 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
