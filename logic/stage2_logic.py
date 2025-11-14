# ==========================================================
# logic/stage2_logic.py — FIXED VERSION (Stage3 전환 포함)
# ==========================================================
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage2 import adjacent_nodes_stage2


# ----------------------------------------------------------
# Stage2 다음 중심/타깃 업데이트
# ----------------------------------------------------------
def update_next_nodes_stage2(state, bomb_positions, stage2_adj, exploded_node, source2):

    linked = list(adjacent_nodes_stage2(exploded_node, bomb_positions))
    print(f"   📎 연결된 폭탄: {linked}")

    # ✔ 연결 4개면 정상 중심
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

    # ❌ 4개 아니면 → (2,2)로 리셋
    print(f"   ❌ 중심 후보 연결 부족 → 중심을 {source2} 으로 리셋")

    reset_center = source2

    linked = list(adjacent_nodes_stage2(reset_center, bomb_positions))
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

    print_round_header("새 라운드 시작 (Stage 2)")

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


# ----------------------------------------------------------
# Stage2 폭발 처리 (★ Stage3 전환 수정 포함)
# ----------------------------------------------------------
def explode_stage2(state, node, bomb_positions, stage2_adj, source2):

    print_round_header("EXPLODE 처리 (Stage 2)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    print(f"   💥 폭발 발생: {node}")

    update_next_nodes_stage2(state, bomb_positions, stage2_adj, node, source2)

    # 🔥 Stage3 전환 검사 (round_count + 1 기준)
    if state["round_count"] + 1 > state["MAX_ROUNDS"]:
        print("   🚀 Stage 3 전환 준비...")
        state["waiting_stage_change"] = True
        state["stage_transition_timer"] = 2.0  # 2초 후 전환
        return

    # 정상 라운드 증가
    state["round_count"] += 1

    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0


# ----------------------------------------------------------
# Stage2 해제 성공 처리 (★ 동일하게 Stage3 전환 검사 포함)
# ----------------------------------------------------------
def handle_defuse_success_stage2(state, bomb_positions, stage2_adj, node, source2):

    print_round_header("DEFUSE SUCCESS (Stage 2)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0

    # 🔥 Stage3 전환 검사
    if state["round_count"] + 1 > state["MAX_ROUNDS"]:
        print("   🚀 Stage 3 전환 준비...")
        state["waiting_stage_change"] = True
        state["stage_transition_timer"] = 0.01
        return

    state["round_count"] += 1

    update_next_nodes_stage2(state, bomb_positions, stage2_adj, node, source2)

    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
