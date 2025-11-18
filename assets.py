import pygame
from settings import WIDTH, HEIGHT, BOMB_RADIUS

ASSET = "assets/"


# ---------------------------------------------------------
# 🔥 1. 공통: 이미지 로드 + 스케일 함수
# ---------------------------------------------------------
def load_and_scale(name, size=None, alpha=True):
    """이미지 로드 + 선택적 스케일링"""
    path = ASSET + name
    img = pygame.image.load(path)

    img = img.convert_alpha() if alpha else img.convert()

    if size is not None:
        img = pygame.transform.scale(img, size)

    return img


# ---------------------------------------------------------
# 🔥 2. 전체 에셋 로딩을 한 곳에서 처리
# ---------------------------------------------------------
def load_assets():
    assets = {}

    # -------------------------
    # ⭐ UI 이미지
    # -------------------------
    assets["menu"]  = load_and_scale("menu.png", (WIDTH, HEIGHT), alpha=False)
    assets["start"] = load_and_scale("start.png", (400, 200))
    assets["exit"]  = load_and_scale("exit.png", (400, 200))   # ← 추가됨

    # -------------------------
    # ⭐ 폭탄 관련
    # -------------------------
    bomb_size = (BOMB_RADIUS * 2, BOMB_RADIUS * 2)

    assets["black_bomb"] = load_and_scale("black.png", bomb_size)
    assets["red_bomb"]   = load_and_scale("red.png", bomb_size)
    assets["explosion"]  = load_and_scale("bomb.png", (220, 220))
    assets["success"]    = load_and_scale("success.png", (180, 180))

    # -------------------------
    # ⭐ 스테이지 배경
    # -------------------------
    for stage in [1, 2, 3]:
        assets[f"stage{stage}_bg"] = load_and_scale(
            f"stage{stage}_background.png", (WIDTH, HEIGHT), alpha=False
        )

    # -------------------------
    # ⭐ 기타 화면 (Clear / Over / Stage Start)
    # -------------------------
    extra_screens = [
        "game_clear.png", "game_over.png",
        "stage1_start.png", "stage2_start.png", "stage3_start.png"
    ]

    for name in extra_screens:
        key = name.replace(".png", "")
        assets[key] = load_and_scale(name, (WIDTH, HEIGHT), alpha=False)

    return assets
