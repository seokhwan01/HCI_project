# logic/base_logic.py
import random
from stage1 import adjacent_nodes_stage1
from stage2 import adjacent_nodes_stage2
from settings import MAX_ROUNDS
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
def get_candidates(node, stage, bomb_positions, adj_dict):
    if node is None:
        return []

    # 단순하게 adj_dict 그대로 사용 (stage1, stage2, stage3 모두 처리됨)
    adj = adj_dict.get(node, [])

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
        "MAX_ROUNDS": MAX_ROUNDS,

        "success_count": 0,   
        "fail_count": 0,     

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
        "pending_stage_change": False,   # ⭕ 추가됨

        "game_message": "",

        # -------------------------
        # Stage 시작 화면 제어 (⬅ 추가!)
        # -------------------------
        "show_stage_start": False,
        "stage_start_timer": 0.0,
        "stage_start_image": None,

        #마우스 잡아두기
        "mouse_locked_inside": False,

        # -------------------------
        # 로그 기록용 (라운드마다 초기화)
        # -------------------------
        "red_start_time": None,     # 빨간 폭탄 변한 순간
        "cursor_out_time": None,    # 마우스가 처음 폭탄 반경을 벗어난 시점
        "explode_time": None,       # 폭발 발생 시각
        "click_time": None,         # 성공 클릭 시각
        "cursor_out_recorded": False,  # 중복 기록 방지
        "logged_after_explosion": False

        
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
