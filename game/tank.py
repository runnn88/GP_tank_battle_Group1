import pygame
import math
from config import (
    TANK_SPEED,
    ROTATION_SPEED,
    TANK_RADIUS,
    MAX_BULLETS,
    FRIENDLY_FIRE,
    BULLET_COOLDOWN,
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
        self.shoot_cooldown = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            shoot_keys = self.controls.get("shoot")
            if isinstance(shoot_keys, (tuple, list, set)):
                is_shoot = event.key in shoot_keys
            else:
                is_shoot = event.key == shoot_keys

            if is_shoot and self.shoot_cooldown <= 0:
                if len(self.bullets) < MAX_BULLETS:
                    self.shoot()
                    self.shoot_cooldown = BULLET_COOLDOWN

    def update(self, dt, walls, enemy):
        keys = pygame.key.get_pressed()

        # Update shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)

        if keys[self.controls["left"]]:
            self.angle -= ROTATION_SPEED * dt
        if keys[self.controls["right"]]:
            self.angle += ROTATION_SPEED * dt

        direction = pygame.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle))
        )

        # Compute intended velocity along current facing direction
        velocity = pygame.Vector2(0, 0)
        if keys[self.controls["forward"]]:
            velocity += direction * TANK_SPEED
        if keys[self.controls["backward"]]:
            velocity -= direction * TANK_SPEED

        # --- AABB collision: move X then Y and resolve with rects ---
        # Move along X
        self.position.x += velocity.x * dt
        self.resolve_wall_collision(walls, axis="x")

        # Move along Y
        self.position.y += velocity.y * dt
        self.resolve_wall_collision(walls, axis="y")

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
        # Spawn at the tip of the barrel (matches render barrel length)
        barrel_length = self.radius + 15
        spawn = self.position + direction * barrel_length
        self.bullets.append(Bullet(spawn, direction, self))

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

    def circle_collision(self, p1, r1, p2, r2):
        return p1.distance_to(p2) <= (r1 + r2)

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        # Center of the tank on screen (after level offset)
        center = pygame.Vector2(
            self.position.x + offset.x,
            self.position.y + offset.y,
        )

        # Calculate forward and right direction vectors
        direction = pygame.Vector2(
            math.cos(math.radians(self.angle)),
            math.sin(math.radians(self.angle)),
        )
        right = pygame.Vector2(-direction.y, direction.x)

        # --- Body: rotated rectangle ---
        body_length = self.radius * 2.6  # along forward
        body_width = self.radius * 1.6   # across

        half_fwd = direction * (body_length / 2)
        half_right = right * (body_width / 2)

        # 4 corners of the rectangle
        corners = [
            center + half_fwd + half_right,
            center + half_fwd - half_right,
            center - half_fwd - half_right,
            center - half_fwd + half_right,
        ]

        pygame.draw.polygon(
            screen,
            self.color,
            [(c.x, c.y) for c in corners],
        )

        # --- Turret base: circle at center ---
        turret_radius = int(self.radius * 0.8)
        pygame.draw.circle(
            screen,
            (40, 40, 40), # color of the base
            (int(center.x), int(center.y)),
            turret_radius,
        )
        pygame.draw.circle(
            screen,
            self.color,
            (int(center.x), int(center.y)),
            turret_radius - 2,
        )

        # --- Turret barrel ---
        barrel_length = self.radius + 18
        barrel_end = self.position + direction * barrel_length

        pygame.draw.line(
            screen,
            (0, 0, 0),
            center,
            barrel_end + offset,
            4,
        )

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen, offset)

    def get_aabb(self):
        """Axis-aligned bounding box around the circular tank body."""
        size = self.radius * 2
        return pygame.Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            size,
            size,
        )

    def resolve_wall_collision(self, walls, axis):
        """AABB vs AABB resolution: stop tank from passing through walls."""
        rect = self.get_aabb()

        for wall in walls:
            if rect.colliderect(wall.rect):
                # Separate along the axis we just moved
                if axis == "x":
                    if rect.centerx > wall.rect.centerx:
                        # Tank is to the right of wall -> push right
                        self.position.x = wall.rect.right + self.radius
                    else:
                        # Tank is to the left of wall -> push left
                        self.position.x = wall.rect.left - self.radius
                else:  # axis == "y"
                    if rect.centery > wall.rect.centery:
                        # Tank is below wall -> push down
                        self.position.y = wall.rect.bottom + self.radius
                    else:
                        # Tank is above wall -> push up
                        self.position.y = wall.rect.top - self.radius

                # Rebuild rect after adjustment
                rect = self.get_aabb()