import pygame
from config import BULLET_SPEED, BULLET_RADIUS, MAX_BULLET_BOUNCES


class Bullet:
    def __init__(self, position, direction, owner):
        self.position = pygame.Vector2(position)
        self.velocity = direction.normalize() * BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.alive = True
        self.owner = owner
        self.bounce_count = 0

    def update(self, dt, walls):
        old_position = self.position.copy()
        self.position += self.velocity * dt

        for wall in walls:
            if wall.rect.collidepoint(self.position.x, self.position.y):
                # Move back out of the wall before reflecting to avoid "stuck" bounces
                self.position = old_position
                self.reflect(wall.rect)
                self.bounce_count += 1

                if MAX_BULLET_BOUNCES != -1:
                    if self.bounce_count > MAX_BULLET_BOUNCES:
                        self.alive = False

    def reflect(self, rect):
        overlap_left = abs(self.position.x - rect.left)
        overlap_right = abs(self.position.x - rect.right)
        overlap_top = abs(self.position.y - rect.top)
        overlap_bottom = abs(self.position.y - rect.bottom)

        min_overlap = min(overlap_left,
                          overlap_right,
                          overlap_top,
                          overlap_bottom)

        if min_overlap == overlap_left:
            normal = pygame.Vector2(-1, 0)
        elif min_overlap == overlap_right:
            normal = pygame.Vector2(1, 0)
        elif min_overlap == overlap_top:
            normal = pygame.Vector2(0, -1)
        else:
            normal = pygame.Vector2(0, 1)

        self.velocity = self.velocity - 2 * self.velocity.dot(normal) * normal

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (int(self.position.x + offset.x), int(self.position.y + offset.y)),
            self.radius,
        )