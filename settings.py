# settings.py
import pygame

pygame.init()

condition_map = {
    1: [20, 100],
    2: [20, 150],
    3: [30, 100],
    4: [30, 150],
    5: [40, 100],
    6: [40, 150],
}

order_sets = {
    "S1": [1, 2, 6, 3, 5, 4],
    "S2": [2, 3, 1, 4, 6, 5],
    "S3": [3, 4, 2, 5, 1, 6],
    "S4": [4, 5, 3, 6, 2, 1],
    "S5": [5, 6, 4, 1, 3, 2],
    "S6": [6, 1, 5, 2, 4, 3]
}
#2025/11/25 화요일 s3까지 진행 

# -------------------------
# 화면 설정
# -------------------------
WIDTH = 1000
HEIGHT = 1000

# -------------------------
# 폭탄 기본 크기 설정
# -------------------------
BOMB_RADIUS = 40
BOMB_DISTANCE = 150  # 원하는 거리(px), 여기만 수정하면 전체 적용됨

#w최소 50

#라운드 갯수 
MAX_ROUNDS=10

# -------------------------
# 게임 속도
# -------------------------
FPS = 60
# FUSE_SPEED_100 = 12.0
# FUSE_SPEED_150 = 18.0

TARGET_EXPLODE_TIME=0.6
PULSE_SPEED = 2.0
PULSE_COUNT_REQUIRED = 3

# -------------------------
# 파티클 기본값
# -------------------------
SPARK_COLORS = [
    (255,200,80),
    (255,180,50),
    (255,140,40),
]
SPARK_LIFE_MIN = 4
SPARK_LIFE_MAX = 8
SPARK_SPEED_MIN = 1.5
SPARK_SPEED_MAX = 3.0

# -------------------------
# 폰트
# -------------------------
font = pygame.font.SysFont("malgungothic", 38)
small_font = pygame.font.SysFont("malgungothic", 28)
pause_font = pygame.font.SysFont("malgungothic", 55)

# -------------------------
# 마우스 관련
# -------------------------
MOUSE_LOCK_ON_START = True
