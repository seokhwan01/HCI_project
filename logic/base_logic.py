# logic/base_logic.py
import random
from stage1 import adjacent_nodes_stage1
from stage2 import adjacent_nodes_stage2

# ----------------------------------------------------------
# 디버그 출력
# ----------------------------------------------------------
def print_round_header(title, node=None):
    print("\n" + "=" * 60)
    print(f"💣 {title}" + (f" | 폭탄: {node}" if node else ""))    
    print("=" * 60)

# ----------------------------------------------------------
# 후보 계산
# ----------------------------------------------------------
def get_candidates(node, stage, bomb_positions, stage1_adj):
    if node is None:
        return []

    if stage == 1:
        adj = stage1_adj.get(node, [])
    else:
        adj = list(adjacent_nodes_stage2(node, bomb_positions))

    clean = [n for n in adj if n != node]
    print(f"   🔍 후보 추출 → 중심 {node} → 후보: {clean}")
    return clean

# ----------------------------------------------------------
# 초기 상태 생성
# ----------------------------------------------------------
def init_game_state():
    return {
        "state": "menu",
        "stage": 1,
        "round_count": 0,
        "MAX_ROUNDS": 10,

        # 중심 / 타깃
        "current_source": None,
        "target_node": None,

        # 도화선
        "fuse_burning": False,
        "segment_progress": 0,

        # 폭발
        "explosion_timer": 0,
        "explosion_pos": None,

        # 펄스 기본값
        "pulsing": False,
        "pulse_target": None,
        "pulse_timer": 0,
        "pulse_duration": 0.6,

        # 펄스 상태머신
        # 0: 없음
        # 1: 딜레이
        # 2: 펄스 중
        # 3: 펄스 종료 -> 반복 체크
        # 4: 3회 끝 -> 2초 대기
        # 5: 도화선 점화
        "pulse_phase": 0,
        "pulse_delay": 0,

        # 🔥 반드시 필요한 값
        "pulse_count": 0,       # 현재 펄스 횟수
        "pulse_repeat": 3,      # 총 펄스 횟수 (3번 반복)

        # Stage 전환
        "waiting_stage_change": False,
        "stage_transition_timer": 0,

        "game_message": "",
    }

# ----------------------------------------------------------
# 펄스 시작 (펄스 효과만)
# ----------------------------------------------------------
def start_pulse_common(state, node):
    if state.get("target_node") is None:
        print("⚡ start_pulse_common: 타깃 없음 → 자기 자신으로 설정")
        state["target_node"] = node

    print(f"   ⚡ 펄스 시작: {node}")
    state["pulsing"] = True
    state["pulse_target"] = node
    state["pulse_timer"] = 0

# ----------------------------------------------------------
# 다음 타깃 선택 (공통)
# ----------------------------------------------------------
def choose_next_target_common(node, stage, bomb_positions, stage1_adj, cand=None):
    if cand is None:
        cand = get_candidates(node, stage, bomb_positions, stage1_adj)

    if not cand:
        print(f"⚠ 후보 없음 → {node}에서 이동 불가")
        return None

    return random.choice(cand)
