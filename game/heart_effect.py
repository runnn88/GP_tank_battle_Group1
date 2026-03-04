import pygame
import random

class HeartParticle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(
            random.uniform(-30, 30),
            random.uniform(-80, -40)
        )
        self.life = 0.6
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        self.pos += self.velocity * dt
        self.velocity.y += 120 * dt  # gravity nhẹ

    def draw(self, screen):
        alpha = max(0, 255 * (1 - self.timer / self.life))
        heart = pygame.Surface((20, 20), pygame.SRCALPHA)

        pygame.draw.circle(heart, (255, 120, 160, alpha), (6, 8), 6)
        pygame.draw.circle(heart, (255, 120, 160, alpha), (14, 8), 6)
        pygame.draw.polygon(
            heart,
            (255, 120, 160, alpha),
            [(2, 10), (18, 10), (10, 18)]
        )

        screen.blit(heart, self.pos)

    def is_dead(self):
        return self.timer >= self.life