import pygame


class Wall:
    def __init__(self, x, y, size, image=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        draw_rect = self.rect.move(offset.x, offset.y)
        if self.image:
            screen.blit(self.image, draw_rect.topleft)
        else:
            pygame.draw.rect(screen, (100, 100, 100), draw_rect)