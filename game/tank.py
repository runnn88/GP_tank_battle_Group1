import pygame
import math
from config import (
    TANK_SPEED,
    ROTATION_SPEED,
    TANK_RADIUS,
    MAX_BULLETS,
    FRIENDLY_FIRE,
)
from game.bullet import Bullet


class Tank:
    def __init__(self, position, controls, color):
        self.position = pygame.Vector2(position)
        self.angle = 0
        self.controls = controls
        self.color = color

        self.radius = TANK_RADIUS
        self.health = 3
        self.alive = True

        self.bullets = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["shoot"]:
                if len(self.bullets) < MAX_BULLETS:
                    self.shoot()

    def update(self, dt, walls, enemy):
        keys = pygame.key.get_pressed()

        if keys[self.controls["left"]]:
            self.angle -= ROTATION_SPEED * dt
        if keys[self.controls["right"]]:
            self.angle += ROTATION_SPEED * dt

        direction = pygame.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle))
        )

        old_position = self.position.copy()

        if keys[self.controls["forward"]]:
            self.position += direction * TANK_SPEED * dt
        if keys[self.controls["backward"]]:
            self.position -= direction * TANK_SPEED * dt

        # Tank vs Wall blocking
        self.resolve_wall_collision(walls, old_position)

        # Update bullets
        for bullet in self.bullets:
            bullet.update(dt, walls)

            # Bullet vs Tank
            if bullet.alive and enemy.alive:

                if not FRIENDLY_FIRE and bullet.owner == enemy:
                    pass
                else:
                    if self.circle_collision(bullet.position, bullet.radius,
                                            enemy.position, enemy.radius):
                        enemy.take_damage()
                        bullet.alive = False

        self.bullets = [b for b in self.bullets if b.alive]

    def shoot(self):
        direction = pygame.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle))
        )
        spawn = self.position + direction * self.radius
        self.bullets.append(Bullet(spawn, direction, self))

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

    def circle_collision(self, p1, r1, p2, r2):
        return p1.distance_to(p2) <= (r1 + r2)

    def render(self, screen):
        # Draw tank body
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius
        )

        # Calculate forward direction vector
        direction = pygame.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle))
        )

        # Gun barrel end position
        barrel_length = self.radius + 15
        barrel_end = self.position + direction * barrel_length

        # Draw gun barrel
        pygame.draw.line(
            screen,
            (0, 0, 0),  # black barrel
            self.position,
            barrel_end,
            4  # thickness
        )

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)
            
    def resolve_wall_collision(self, walls, old_position):
        for wall in walls:
            closest_x = max(wall.rect.left,
                            min(self.position.x, wall.rect.right))
            closest_y = max(wall.rect.top,
                            min(self.position.y, wall.rect.bottom))

            distance = pygame.Vector2(self.position.x - closest_x,
                                    self.position.y - closest_y)

            if distance.length() < self.radius:
                self.position = old_position
                return