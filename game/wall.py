import pygame

class Wall:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)

    def render(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)