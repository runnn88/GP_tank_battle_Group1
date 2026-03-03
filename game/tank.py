import pygame
import math
from config import (
    TANK_SPEED,
    ROTATION_SPEED,
    TANK_RADIUS,
    MAX_BULLETS,
    FRIENDLY_FIRE,
    BULLET_COOLDOWN,
    TANK_HEALTH,
)
from game.bullet import Bullet
from game.settings_manager import settings
from game.heart_effect import HeartParticle


class Tank:
    def __init__(self, 
                 position, 
                 controls, 
                 color,
                 turret_left_key_name=None,
                 turret_right_key_name=None):
        # ---------------------------
        # Core Transform
        # ---------------------------
        self.position = pygame.Vector2(position)
        self.angle = 0
        self.turret_angle = 0

        # ---------------------------
        # Controls
        # ---------------------------
        self.controls = controls
        self.turret_left_key_name = turret_left_key_name
        self.turret_right_key_name = turret_right_key_name

        # ---------------------------
        # Visual / Identity
        # ---------------------------
        self.color = color
        self.radius = TANK_RADIUS
        self.effects = []  # List of active visual effects (e.g. heart particles)

        # ---------------------------
        # Gameplay State
        # ---------------------------
        self.health = TANK_HEALTH
        self.max_health = TANK_HEALTH
        self.alive = True

        # ---------------------------
        # Shooting
        # ---------------------------
        self.bullets = []
        self.shoot_cooldown = 0.0
        self.flash_duration = 0.1  # Thời gian flash khi bắn
        self.flash_timer = 0.0

        # ---------------------------
        # Explosion and Flash Effects
        # ---------------------------
        self.explosions = []  # Danh sách hiệu ứng nổ
        self.explosion_image = pygame.image.load("assets/explosion2.png").convert_alpha()
        self.death_timer = 0.0

        self.grow_time = 0.4
        self.hold_time = 1.4
        self.fade_time = 0.7
        self.death_duration = self.grow_time + self.hold_time + self.fade_time
        # self.death_duration = 1.0  # thời gian hiệu ứng
        self.is_dying = False

        # ---------------------------
        # Sounds
        # ---------------------------
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.mp3")
        self.hit_sound = pygame.mixer.Sound("assets/sounds/shoot.mp3")
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.mp3")

        # Load sprites for body and turret
        if color == (0, 200, 0):
            body_path = "assets/body_5.png"
            turret_path = "assets/blue_turret.png"
        else:
            body_path = "assets/body_6.png"
            turret_path = "assets/pink_turret_1.png"

        base_size = int(self.radius * 2.6)
        self.body_image = pygame.image.load(body_path).convert_alpha()
        self.body_image = pygame.transform.scale(
            self.body_image, (base_size, base_size)
        )

        # Load turret sprite and scale with aspect ratio preserved
        self.turret_image = pygame.image.load(turret_path).convert_alpha()
        orig_w, orig_h = self.turret_image.get_size()
        # Scale so the longest side matches ~70% of body size
        max_side = max(orig_w, orig_h)
        scale = (base_size * 0.9) / max_side
        new_size = (int(orig_w * scale), int(orig_h * scale))
        self.turret_image = pygame.transform.scale(self.turret_image, new_size)
        

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
        # --- BODY ROTATION ---
        if keys[self.controls["left"]]:
            self.angle -= ROTATION_SPEED * dt
        if keys[self.controls["right"]]:
            self.angle += ROTATION_SPEED * dt

        # --- TURRET ROTATION ---
        if settings.independent_turret:
            if self.turret_left_key_name:
                if keys[settings.keybinds[self.turret_left_key_name]]:
                    self.turret_angle -= ROTATION_SPEED * dt

            if self.turret_right_key_name:
                if keys[settings.keybinds[self.turret_right_key_name]]:
                    self.turret_angle += ROTATION_SPEED * dt
        else:
            self.turret_angle = self.angle

        # Update shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)

        if keys[self.controls["left"]]:
            self.angle -= ROTATION_SPEED * dt
        if keys[self.controls["right"]]:
            self.angle += ROTATION_SPEED * dt
        if not settings.independent_turret:
            self.turret_angle = self.angle  # Turret follows body if not independent

        # In our sprites, angle 0 points "up", so shift by -90 degrees
        move_rad = math.radians(self.angle - 90)
        direction = pygame.Vector2(
            math.cos(move_rad),
            math.sin(move_rad),
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
            if bullet.alive: 
                # --- Bullet hits enemy tank ---
                if enemy.alive:
                    if self.circle_collision(
                        bullet.position, bullet.radius,
                        enemy.position, enemy.radius):
                        # --- Allow friendly fire if enabled, or if bullet owner is not the enemy ---
                        if settings.friendly_fire or bullet.owner != enemy:
                            enemy.take_damage()
                            bullet.alive = False
                            bullet.sparks.append((bullet.position.copy(), 0))  # Thêm hiệu ứng tia lửa
                
                # --- Bullet hits self ---
                if self.alive and bullet.owner == self:
                    if settings.bullet_can_hit_self:
                        if self.circle_collision(
                            bullet.position, bullet.radius,
                            self.position, self.radius
                        ):
                            self.take_damage()
                            bullet.alive = False
                            bullet.sparks.append((bullet.position.copy(), 0))
                        

        self.bullets = [b for b in self.bullets if b.alive]

        for effect in self.effects:
            effect.update(dt)

        self.effects = [e for e in self.effects if not e.is_dead()]

        if self.flash_timer > 0:
            # self.flash_timer = max(0.0, self.flash_timer - dt)
            self.flash_timer -= dt

        self.explosions = [(pos, timer + dt) for pos, timer in self.explosions if timer + dt < 5.0]
        if self.is_dying:
            self.death_timer += dt
            if self.death_timer >= self.death_duration:
                self.alive = False
                # self.death_timer += dt

    def shoot(self):
        # Use same direction convention as movement (0 degrees = up)
        shoot_rad = math.radians(self.turret_angle - 90)
        direction = pygame.Vector2(
            math.cos(shoot_rad),
            math.sin(shoot_rad),
        )
        # direction = pygame.Vector2(
        #     math.cos(math.radians(self.turret_angle)),
        #     math.sin(math.radians(self.turret_angle))
        # )

        # --- Bullet spawns at the end of the turret barrel, not the center of the tank ---
        barrel_length = self.radius + 15
        spawn = self.position + direction * barrel_length
        self.bullets.append(Bullet(spawn, direction, self))

        # --- Trigger flash effect and sound ---
        self.flash_timer = self.flash_duration  # Kích hoạt hiệu ứng flash
        self.shoot_sound.play()  # Phát âm thanh bắn

    def take_damage(self):
        self.effects.append(HeartParticle(self.position.copy()))  # Thêm hiệu ứng trái tim khi bị bắn trúng

        self.health -= 20
        self.hit_sound.play()
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            # self.alive = False  # Vẫn alive trong quá trình hiệu ứng nổ, sẽ set False sau khi hiệu ứng kết thúc
            self.death_timer = 0.0
            self.explosion_sound.play()
        # if self.health <= 0:
        #     self.explosions.append((self.position.copy(), 0))  # Thêm hiệu ứng nổ
        #     self.explosion_sound.play()
        #     self.alive = False
            # self.explosions.append((self.position.copy(), 0))  # Thêm hiệu ứng nổ
            # self.explosion_sound.play()

    def circle_collision(self, p1, r1, p2, r2):
        return p1.distance_to(p2) <= (r1 + r2)

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        # Center of the tank on screen (after level offset)
        center = pygame.Vector2(
            self.position.x + offset.x,
            self.position.y + offset.y,
        )
        # Nếu đang chết → vẽ explosion animation
        if self.is_dying:
            t = self.death_timer
            progress = min(1.0, t / self.death_duration)

            # -----------------
            # SCALE + ALPHA đồng bộ explosion
            # -----------------
            if t < self.grow_time:
                grow_progress = t / self.grow_time
                scale = 0.5 + grow_progress * 1.5
                alpha = 255

            elif t < self.grow_time + self.hold_time:
                scale = 2.0
                alpha = 255

            else:
                fade_progress = (t - self.grow_time - self.hold_time) / self.fade_time
                scale = 2.0
                alpha = max(0, 255 * (1 - fade_progress))

            size = int(self.radius * 4 * scale)

            explosion = pygame.transform.scale(
                self.explosion_image,
                (size, size)
            )
            explosion.set_alpha(alpha)

            rect = explosion.get_rect(center=center)
            screen.blit(explosion, rect)

            # -----------------
            # BOOM text (sync 100%)
            # -----------------
            font_size = int(35 * scale)
            boom_font = pygame.font.Font("assets/fonts/Star Crush.ttf", font_size)

            text = "BOOM"
            text_surface = boom_font.render(text, True, (255, 70, 70))
            text_surface.set_alpha(alpha)

            outline_surface = boom_font.render(text, True, (0, 0, 0))
            outline_surface.set_alpha(alpha)

            text_rect = text_surface.get_rect(center=center)

            screen.blit(outline_surface, text_rect.move(-3, 0))
            screen.blit(outline_surface, text_rect.move(3, 0))
            screen.blit(outline_surface, text_rect.move(0, -3))
            screen.blit(outline_surface, text_rect.move(0, 3))
            screen.blit(text_surface, text_rect)

            return

        # Tính toán vị trí mới cho turret
        # --- BODY ---
        rotated_body = pygame.transform.rotate(self.body_image, -self.angle)
        body_rect = rotated_body.get_rect(center=center)
        screen.blit(rotated_body, body_rect.topleft)

        # --- TURRET (independent) ---
        rotated_turret = pygame.transform.rotate(self.turret_image, -self.turret_angle)
        turret_rect = rotated_turret.get_rect(center=center)
        screen.blit(rotated_turret, turret_rect.topleft)

        if self.flash_timer > 0:
            flash_pos = center + pygame.Vector2(math.cos(math.radians(self.angle - 90)),
                                                math.sin(math.radians(self.angle - 90))) * (self.radius + 15)
            pygame.draw.circle(screen, (255, 255, 0), (int(flash_pos.x), int(flash_pos.y)), 5)

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen, offset)

        # Draw effects
        for effect in self.effects:
            effect.draw(screen)

        # Hiển thị hiệu ứng nổ
        for pos, timer in self.explosions:
            explosion_size = int(30 * timer)  # Kích thước nổ tăng dần
            alpha = max(255 - int(255 * timer), 0)  # Giảm độ trong suốt
            explosion_surface = pygame.Surface((explosion_size * 2, explosion_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 100, 0, alpha), (explosion_size, explosion_size), explosion_size)
            screen.blit(explosion_surface, (pos.x + offset.x - explosion_size, pos.y + offset.y - explosion_size))

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