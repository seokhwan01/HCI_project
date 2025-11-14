import pygame
from settings import WIDTH, HEIGHT, BOMB_RADIUS

ASSET = "assets/"

# UI 이미지 로딩 (메뉴, 시작 버튼)
def load_ui_images():
    menu = pygame.image.load(ASSET + "menu.png").convert()
    menu = pygame.transform.scale(menu, (WIDTH, HEIGHT))

    start_img = pygame.image.load(ASSET + "start.png").convert_alpha()
    start_img = pygame.transform.scale(start_img, (400, 200))

    return menu, start_img


# 폭탄 관련 이미지 로딩
def load_bomb_images():
    black_bomb = pygame.image.load(ASSET + "black.png").convert_alpha()
    red_bomb   = pygame.image.load(ASSET + "red.png").convert_alpha()
    explosion  = pygame.image.load(ASSET + "bomb.png").convert_alpha()

    black_bomb = pygame.transform.scale(black_bomb, (BOMB_RADIUS*2, BOMB_RADIUS*2))
    red_bomb   = pygame.transform.scale(red_bomb,   (BOMB_RADIUS*2, BOMB_RADIUS*2))
    explosion  = pygame.transform.scale(explosion,  (220, 220))

    return black_bomb, red_bomb, explosion


def load_background(stage):
    bg = pygame.image.load(ASSET + f"stage{stage}_background.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    return bg
