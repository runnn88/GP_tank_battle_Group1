# preview_shapes.py
import pygame
from game.tank import Tank
from game.wall import Wall
from config import TANK_RADIUS, TILE_SIZE

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

# Tạo tank test ở giữa màn hình
tank = Tank((200, 150), controls={}, color=(0, 200, 0))
tank.angle = 0  # hướng nòng súng

# Tạo 1 tường test
wall = Wall(100, 100, TILE_SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    wall.render(screen)
    tank.render(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()