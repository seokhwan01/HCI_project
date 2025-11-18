# logic/stage1_logic.py
from logic.base_logic import (
    print_round_header, get_candidates,
    choose_next_target_common
)
from stage1 import adjacent_nodes_stage1
from log_writer import write_log, utc_now
from settings import BOMB_RADIUS, BOMB_DISTANCE
W = BOMB_RADIUS * 2
A = BOMB_DISTANCE
# ----------------------------------------------------------
# Stage1 중심/타깃 업데이트 (고정 규칙)
# ----------------------------------------------------------
def update_next_nodes_stage1(state, bomb_positions, stage1_adj, exploded_node, source1):

    # 1) 우선 폭발한 노드를 중심 후보로 사용
    linked = list(adjacent_nodes_stage1(exploded_node, bomb_positions))
    print(f"   📎 중심 후보 {exploded_node} 의 연결 수: {len(linked)} → {linked}")

    # 연결 3개면 정상 중심
    if len(linked) == 3:
        print(f"   ✅ 중심 후보 {exploded_node} 연결 3개 → 중심 확정")
        state["current_source"] = exploded_node

        cand = get_candidates(exploded_node, 1, bomb_positions, stage1_adj)
        if cand:
            state["target_node"] = choose_next_target_common(
                exploded_node, 1, bomb_positions, stage1_adj, cand)
        else:
            print("   ⚠ 타깃 후보 없음 → 자기 자신 설정")
            state["target_node"] = exploded_node

        state["connected_targets"] = linked
        print(f"   🎯 타깃 = {state['target_node']}")
        return

    # ------------------------------------------------------
    # 2) 연결 3개 아니면 무조건 (2,2) 리셋
    # ------------------------------------------------------
    print("   ❌ 중심 후보 연결 부족 → 중심을 (2,2)으로 리셋")

    reset_center = source1  # (2,2)
    linked = list(adjacent_nodes_stage1(reset_center, bomb_positions))

    state["current_source"] = reset_center
    state["connected_targets"] = linked

    cand = get_candidates(reset_center, 1, bomb_positions, stage1_adj)

    if cand:
        state["target_node"] = choose_next_target_common(
            reset_center, 1, bomb_positions, stage1_adj, cand)
    else:
        print("   ⚠ 리셋 중심에서도 타깃 없음 → 자기 자신 설정")
        state["target_node"] = reset_center

    print(f"   🔁 리셋 중심 = {reset_center}")
    print(f"   🎯 타깃 = {state['target_node']}")
    return



# ----------------------------------------------------------
# Stage1 새 라운드 시작
# ----------------------------------------------------------
def start_new_round_stage1(state, bomb_positions, stage1_adj, source1):

    print_round_header("새 라운드 시작 (Stage 1)")
    state["mouse_locked_inside"] = True   # 🔒 라운드 시작 즉시 잠금
    state["red_start_time"] = None
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False
    state["explode_time"] = None
    state["click_time"] = None


    # 펄스 초기화
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0

    # 중심 고정
    state["current_source"] = source1
    state["fuse_burning"] = False
    state["segment_progress"] = 0

    # 타깃 선정
    cand = get_candidates(source1, 1, bomb_positions, stage1_adj)
    if cand:
        state["target_node"] = choose_next_target_common(source1, 1, bomb_positions, stage1_adj, cand)
    else:
        print("⚠ 시작 라운드 타깃 없음 → 자기 자신")
        state["target_node"] = source1

    print(f"   💣 중심 = {state['current_source']}")
    print(f"   🎯 타깃 = {state['target_node']}")


# ----------------------------------------------------------
# Stage1 폭발 처리 (완전 수정)
# ----------------------------------------------------------
def explode_stage1(state, node, bomb_positions, stage1_adj, source1):

    state["explode_time"] = utc_now()

    write_log(
        state["log_file"],
        N=3,
        trial=state["round_count"],
        W=W,
        A=A,
        red_start_time=state.get("red_start_time",""),
        cursor_out_time=state.get("cursor_out_time",""),
        explode_time=state["explode_time"],
        click_time="",       # 실패이므로 빈 칸
        success=0
    )

    print_round_header("EXPLODE 처리 (Stage 1)", node)

    # 1) 이펙트 먼저
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["explosion_timer"] = 0.6
    state["explosion_pos"] = bomb_positions[node]

    print(f"   💥 폭발 발생: {node}")
    state["mouse_locked_inside"] = False

    # 2) 중심/타깃 업데이트
    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    # 3) 타깃 유효성 보정
    if state["target_node"] is None:
        print("   ⚠ target_node None → 자기 자신으로 보정")
        state["target_node"] = state["current_source"]

    # 4) 라운드 증가
    state["fail_count"] += 1
    state["round_count"] += 1

    #로그 초기화
    # 여기 추가!
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 5) 전환 검사
    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 2 전환 준비...")
        state["pending_stage_change"] = True
        return

    # 6) 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0
    state["pulse_count"] = 0



# ----------------------------------------------------------
# Stage1 성공 처리 (완전 수정)
# ----------------------------------------------------------
def handle_defuse_success_stage1(state, bomb_positions, stage1_adj, node, source1):
    # 클릭 성공 시점 기록
    state["click_time"] = utc_now()

    # 여기서 로그 한 줄 기록
    write_log(
        state["log_file"],
        N=3,                          # Stage1 → 연결 3개
        trial=state["round_count"],   # 현재 라운드
        W=W,
        A=A,                
        red_start_time=state.get("red_start_time",""),
        cursor_out_time=state.get("cursor_out_time",""),
        explode_time="",              # 성공했으므로 없음
        click_time=state["click_time"],
        success=1
    )

    print_round_header("DEFUSE SUCCESS (Stage 1)", node)

    # 1) 이펙트
    state["fuse_burning"] = False
    state["segment_progress"] = 0
    state["success_timer"] = 0.6
    state["success_pos"] = bomb_positions[node]

    state["mouse_locked_inside"] = False

    # 2) 중심/타깃 갱신
    update_next_nodes_stage1(state, bomb_positions, stage1_adj, node, source1)

    if state["target_node"] is None:
        print("   ⚠ target_node None → 자기 자신으로 보정")
        state["target_node"] = state["current_source"]

    # 3) 라운드 증가
    state["round_count"] += 1
    state["success_count"] += 1

    #로그 초기화
    # 여기 추가!
    state["cursor_out_time"] = None
    state["cursor_out_recorded"] = False

    print(f"   ➕ round = {state['round_count']} / MAX = {state['MAX_ROUNDS']}")

    # 4) 전환 검사
    if state["round_count"] >= state["MAX_ROUNDS"]:
        print("   🚀 Stage 2 전환 준비...")
        state["pending_stage_change"] = True
        return

    # 5) 다음 라운드 준비
    state["pulse_phase"] = 1
    state["pulse_delay"] = 2.0 
    state["pulse_count"] = 0
