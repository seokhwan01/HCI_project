# settings.py
import pygame

pygame.init()

# -------------------------
# 화면 설정
# -------------------------
WIDTH = 1000
HEIGHT = 700

# -------------------------
# 폭탄 기본 크기 설정
# -------------------------
BOMB_RADIUS = 30

# -------------------------
# 스테이지 구조
# -------------------------
MAX_ROUNDS_PER_STAGE = 10

# -------------------------
# 게임 속도
# -------------------------
FPS = 60
FUSE_SPEED = 14.0
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
