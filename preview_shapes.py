# preview_shapes.py
import pygame
from explosion import Explosion
from game.wall import Wall
from config import TILE_SIZE

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

# Tạo hiệu ứng nổ test
explosion = Explosion((200, 150), duration=2.0, max_size=50)

# Tạo 1 tường test
wall = Wall(100, 100, TILE_SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Cập nhật hiệu ứng nổ
    dt = clock.tick(60) / 1000.0  # Delta time
    explosion.update(dt)

    # Vẽ màn hình
    screen.fill((30, 30, 30))
    wall.render(screen)
    explosion.render(screen)
    pygame.display.flip()

pygame.quit()