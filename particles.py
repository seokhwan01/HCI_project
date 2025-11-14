import pygame
import random
import math

# 모든 입자(불꽃 조각)를 저장하는 전역 리스트
# 각 입자: [x, y, vx, vy, life, color]
particles = []


def spawn_spark(x, y, dir_vec, count=8):
    """
    불꽃 파티클을 여러 개 생성하는 함수.
    x, y        : 파티클을 생성할 위치(보통 도화선 끝, 폭발 지점 등)
    dir_vec     : (dx, dy) 방향 벡터 — 불꽃을 뿜는 기본 방향
    count       : 생성할 파티클 수
    """

    dx, dy = dir_vec
    l = math.hypot(dx, dy)  # 방향 벡터 길이 계산

    # 방향 벡터 정규화 (길이를 1로 만듦)
    if l != 0:
        dx /= l
        dy /= l
    else:
        dx, dy = 1, 0  # 길이가 0이면 기본 방향을 오른쪽으로 설정

    for _ in range(count):
        # -0.4 ~ 0.4 rad(약 ±23°) 랜덤 각도 — 기본 방향에서 좌우로 퍼뜨리기
        ang = random.uniform(-0.4, 0.4)

        # 회전 행렬 적용하여 기본 방향 벡터(dx,dy)를 약간 회전시킴
        vx = dx * math.cos(ang) - dy * math.sin(ang)
        vy = dx * math.sin(ang) + dy * math.cos(ang)

        # 속도 크기 랜덤 적용 (1.5~3.0배)
        vx *= random.uniform(1.5, 3.0)
        vy *= random.uniform(1.5, 3.0)

        # 약간 위로 튀는 효과 (중력 방향 y+라서 y속도 약간 감소)
        vy -= 0.5

        # 파티클 생명 (불꽃 크기에도 영향, 시간이 지나면 사라짐)
        life = random.uniform(4, 8)

        # 색상 랜덤 — 노란불, 주황불 계열
        col = random.choice([
            (255, 200, 80),
            (255, 180, 50),
            (255, 140, 40)
        ])

        # 파티클 추가
        particles.append([x, y, vx, vy, life, col])


def update_particles(surface):
    """
    생성된 파티클들을 업데이트하고 화면(surface)에 그리는 함수.
    - 위치 이동
    - 중력 적용
    - 수명 감소
    - 화면에 작은 원으로 그리기
    """
    global particles
    new_list = []  # 살아있는 파티클만 여기 다시 넣음

    for x, y, vx, vy, life, col in particles:
        life -= 0.2  # 파티클 수명 감소 (프레임마다)

        if life > 0:
            # 위치 이동
            x += vx
            y += vy

            # 중력 적용 — y축 속도 증가 (아래로 떨어짐)
            vy += 0.2

            # 불꽃 크기 = life/2 → 시간이 지날수록 점점 작아짐
            pygame.draw.circle(surface, col, (int(x), int(y)), int(life / 2))

            # 계속 살아있는 파티클만 다시 저장
            new_list.append([x, y, vx, vy, life, col])

    # 새로운 리스트로 교체해 죽은 파티클 전부 제거
    particles = new_list
