# ==========================================================
# logic/stage3_logic.py — Stage3 로직 (6연결 헥사곤 전용)
# ==========================================================
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage3 import adjacent_nodes_stage3


# 중심 기본값
DEFAULT_CENTER_STAGE3 = (2, 2)


# ----------------------------------------------------------
# Stage3 중심/타깃 재선정
# ----------------------------------------------------------
def update_next_nodes_stage3(state, bomb_positions, stage3_adj, exploded_node):

    linked = list(adjacent_nodes_stage3(exploded_node, bomb_positions))
    print(f"   📎 연결된 폭탄: {linked}")

    # 중심 = 방금 터진 노드
    state["current_source"] = exploded_node
    state["connected_targets"] = linked

    # ✔ 연결 6개면 정상 중심
    if len(linked) == 6:
        cand = get_candidates(exploded_node, 3, bomb_positions, stage3_adj)
        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 3, bomb_positions, stage3_adj, cand)
            print(f"   🎯 타깃 = {state['target_node']}")
            return

    # ❌ 연결 부족 → 기본 중심으로 복귀
    print(f"   🔁 연결 부족 → 중심을 {DEFAULT_CENTER_STAGE3}으로 리셋")

    state["current_source"] = DEFAULT_CENTER_STAGE3
    cand = get_candidates(DEFAULT_CENTER_STAGE3, 3, bomb_positions, stage3_adj)

    if cand:
        state["target_node"] = choose_next_target_common(
            DEFAULT_CENTER_STAGE3, 3, bomb_positions, stage3_adj, cand)
    else:
        state["target_node"] = DEFAULT_CENTER_STAGE3

    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage3 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage3(state, bomb_positions, stage3_adj, source3):

    print_round_header("새 라운드 시작 (Stage 3)")

    # 펄스 초기화
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0

    # 중심 초기화
    state["current_source"] = source3
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    # 타깃 선정
    cand = get_candidates(source3, 3, bomb_positions, stage3_adj)
    state["target_node"] = choose_next_target_common(
        source3, 3, bomb_positions, stage3_adj, cand)

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage3 폭발 처리
# ----------------------------------------------------------
def explode_stage3(state, node, bomb_positions, stage3_adj):

    print_round_header("EXPLODE 처리 (Stage 3)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    print(f"   💥 폭발 발생: {node}")

    update_next_nodes_stage3(state, bomb_positions, stage3_adj, node)

    state["round_count"] += 1

    # Stage3 종료 조건
    if state["round_count"] > state["MAX_ROUNDS"]:
        print("   🎉 Stage 3 완료! 게임 종료 준비")
        state["game_finished"] = True
        return

    # 다음 라운드 펄스 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0


# ----------------------------------------------------------
# Stage3 해제 성공 처리
# ----------------------------------------------------------
def handle_defuse_success_stage3(state, bomb_positions, stage3_adj, node):

    print_round_header("DEFUSE SUCCESS (Stage 3)", node)

    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0

    state["round_count"] += 1

    update_next_nodes_stage3(state, bomb_positions, stage3_adj, node)

    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0
