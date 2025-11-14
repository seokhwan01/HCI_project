import pygame
import math
from particles import spawn_spark

# -------------------------------------------------------
# 도화선 그리기 (Stage1 / Stage2 공용)
# -------------------------------------------------------
def draw_fuse(surface, a_pos, b_pos, progress=None, active=False):
    """
    surface : pygame 화면(screen)
    a_pos   : 시작 점 (x,y)
    b_pos   : 끝 점 (x,y)
    progress: 0.0~1.0 (도화선 불이 이동한 비율)
    active  : True일 때만 스파크 및 불빛 애니메이션 실행
    """

    sx, sy = a_pos
    ex, ey = b_pos

    # 1) 기본 도화선 (갈색)
    pygame.draw.line(surface, (130, 90, 50), (sx, sy), (ex, ey), 8)

    # progress 없으면 점화 애니메이션 없음
    if progress is None:
        return

    # 2) 점화된 부분 (노란 라인)
    cx = sx + (ex - sx) * progress
    cy = sy + (ey - sy) * progress

    pygame.draw.line(surface, (240, 200, 80), (sx, sy), (cx, cy), 6)

    # 3) active=True이면 스파크 / 불빛 그리기
    if active:
        # 불빛 원 2중
        pygame.draw.circle(surface, (255, 200, 80), (int(cx), int(cy)), 10)
        pygame.draw.circle(surface, (255, 80, 0), (int(cx), int(cy)), 6)

        # 스파크는 도화선 반대 방향으로 튀도록
        dir_vec = (sx - ex, sy - ey)

        spawn_spark(cx, cy, dir_vec, 6)
