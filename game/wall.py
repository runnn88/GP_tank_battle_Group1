import pygame

class Wall:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        draw_rect = self.rect.move(offset.x, offset.y)
        pygame.draw.rect(screen, (100, 100, 100), draw_rect)