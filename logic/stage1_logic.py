# logic/stage1_logic.py
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage1 import adjacent_nodes_stage1


# ----------------------------------------------------------
# Stage1 중심/타깃 업데이트 (너의 규칙 적용)
# ----------------------------------------------------------
def update_next_nodes_stage1(state, bomb_positions, stage1_adj, exploded_node, source1):

    # ------------------------------------------------------
    # 1) 우선 폭발한 노드를 중심 후보로 삼는다.
    # ------------------------------------------------------
    linked = list(adjacent_nodes_stage1(exploded_node, bomb_positions))
    print(f"   📎 중심 후보 {exploded_node} 의 연결 수: {len(linked)} → {linked}")

    # 중심 후보가 연결 3개를 만족하면 → 그대로 중심 확정
    if len(linked) == 3:
        print(f"   ✅ 중심 후보 {exploded_node} 연결 3개 → 중심 확정")
        state["current_source"] = exploded_node
        cand = get_candidates(exploded_node, 1, bomb_positions, stage1_adj)

        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 1, bomb_positions, stage1_adj, cand)
        else:
            state["target_node"] = exploded_node

        state["connected_targets"] = linked
        print(f"   🎯 타깃 = {state['target_node']}")
        return

    # ------------------------------------------------------
    # 2) 폭발한 노드가 연결 3개가 아니라면 → (2,3)으로 강제 리셋
    # ------------------------------------------------------
    print("   ❌ 중심 후보 연결 부족 → 중심을 (2,3)으로 리셋")

    reset_center = source1  # 보통 (2,3)
    linked = list(adjacent_nodes_stage1(reset_center, bomb_positions))

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 1, bomb_positions, stage1_adj)
    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 1, bomb_positions, stage1_adj, cand)
    else:
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")



# ----------------------------------------------------------
# Stage1 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage1(state, bomb_positions, stage1_adj, source1):

    print_round_header("새 라운드 시작 (Stage 1)")

    # 2초 대기 후 펄스 시작
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0

    # 중심 고정
    state["current_source"] = source1
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    # 타깃 선정
    cand = get_candidates(source1, 1, bomb_positions, stage1_adj)
    state["target_node"] = choose_next_target_common(source1, 1, bomb_positions, stage1_adj, cand)

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage1 폭발 처리
# ----------------------------------------------------------
def explode_stage1(state, node, bomb_positions, stage1_adj, source1):

    print_round_header("EXPLODE 처리 (Stage 1)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0

    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    print(f"   💥 폭발 발생: {node}")

    # 중심/타깃 업데이트
    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    # ------------------------------------------------------
    # 🔥 Stage1 → Stage2 전환 검사 (라운드 +1을 먼저 보는 방식)
    # ------------------------------------------------------
    if state["round_count"] + 1 > state["MAX_ROUNDS"]:
        print("   🚀 Stage 2 전환 준비...")
        state["waiting_stage_change"] = True
        state["stage_transition_timer"] = 2.0   # 즉시 전환
        return

    # ------------------------------------------------------
    # 문제 없으면 라운드 증가
    # ------------------------------------------------------
    state["round_count"] += 1

    # 2초 후 펄스 재시작
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0



# ----------------------------------------------------------
# Stage1 성공 처리
# ----------------------------------------------------------
def handle_defuse_success_stage1(state, bomb_positions, stage1_adj, node, source1):

    print_round_header("DEFUSE SUCCESS (Stage 1)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0

    state["round_count"] += 1

    # 다음 중심/타깃은 "해제 성공한 노드"
    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    # 🔥 Stage1 → Stage2 전환 검사 (추가 필요!!)
    if state["round_count"] > state["MAX_ROUNDS"]:
        print(" Stage 2 전환 준비...")
        state["waiting_stage_change"] = True
        state["stage_transition_timer"] = 0.01
        return

    # 2초 후 다시 펄스
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
