import pygame


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)

    def render(self, screen, p1, p2):
        text1 = self.font.render(f"P1 HP: {p1.health}", True, (0, 255, 0))
        text2 = self.font.render(f"P2 HP: {p2.health}", True, (255, 0, 0))

        screen.blit(text1, (20, 20))
        screen.blit(text2, (800, 20))