import pygame
import math
import random

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
        self.turret_length = 15  # Khoảng cách từ tâm tank đến đầu nòng, dùng để tính vị trí spawn đạn và hiệu ứng flash chính xác

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
        self.explosion_image = pygame.image.load("assets/image/explosion2.png").convert_alpha()
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

        # ---------------------------
        # Power-ups
        # ---------------------------
        self.active_powerups = {}
        self.base_speed = TANK_SPEED
        self.speed = TANK_SPEED
        self.shield_active = False

        # ---------------------------
        # Visual Feedback Effects
        # ---------------------------
        self.pickup_flash_timer = 0.0
        self.pickup_flash_duration = 0.4
        self.sparks = []  # List of spark particles for shooting effect 

        self.shield_warning_time = 1.5   # thời gian trước khi hết để nhấp nháy

        # Orbit power-up visuals
        self.orbit_effects = []  # list các icon xoay quanh

        # Load sprites for body and turret
        if color == (150, 200, 255):
            body_path = "assets/image/body_5.png"
            turret_path = "assets/image/blue_turret.png"
        else:
            body_path = "assets/image/body_6.png"
            turret_path = "assets/image/pink_turret_1.png"

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

    def apply_powerup(self, type_, duration):
        self.active_powerups[type_] = duration
        self.pickup_flash_timer = self.pickup_flash_duration  # Kích hoạt hiệu ứng flash khi nhặt power-up

        if type_ == "speed":
            self.speed = self.base_speed * 1.5
            self.create_orbit_effect(type_)

        elif type_ == "shield":
            self.shield_active = True

        elif type_ == "triple":
            self.create_orbit_effect(type_)

    def create_orbit_effect(self, type_):
        count = 4
        for i in range(count):
            self.orbit_effects.append({
                "type": type_,
                "angle": (360 / count) * i,
                "radius": self.radius + 25
            })

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
        # Update active powerups
        expired = []

        # Pickup flash countdown
        if self.pickup_flash_timer > 0:
            self.pickup_flash_timer -= dt

        for key in self.active_powerups:
            self.active_powerups[key] -= dt
            if self.active_powerups[key] <= 0:
                expired.append(key)

        for key in expired:
            del self.active_powerups[key]

            if key == "speed":
                self.speed = self.base_speed

            elif key == "shield":
                self.shield_active = False
        
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

        # In our sprites, angle 0 points "up", so shift by -90 degrees
        move_rad = math.radians(self.angle - 90)
        direction = pygame.Vector2(
            math.cos(move_rad),
            math.sin(move_rad),
        )

        # Compute intended velocity along current facing direction
        velocity = pygame.Vector2(0, 0)
        if keys[self.controls["forward"]]:
            velocity += direction * self.speed
        if keys[self.controls["backward"]]:
            velocity -= direction * self.speed

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

        for spark in self.sparks[:]:
            spark["timer"] += dt
            spark["pos"] += spark["vel"] * dt
            spark["vel"] *= 0.9  # chậm dần
            spark["rot"] += spark["rot_speed"] * dt

            if spark["timer"] >= spark["life"]:
                self.sparks.remove(spark)

        self.explosions = [(pos, timer + dt) for pos, timer in self.explosions if timer + dt < 5.0]
        if self.is_dying:
            self.death_timer += dt
            if self.death_timer >= self.death_duration:
                self.alive = False
                # self.death_timer += dt

        # Update orbit effects
        new_orbits = []
        for effect in self.orbit_effects:
            if effect["type"] in self.active_powerups:
                effect["angle"] += 180 * dt  # tốc độ xoay
                new_orbits.append(effect)

        self.orbit_effects = new_orbits

    def draw_shield(self, screen, center):
        remaining = self.active_powerups.get("shield", 0)

        # Nếu gần hết → nhấp nháy
        blink = False
        if remaining <= self.shield_warning_time:
            blink = int(remaining * 8) % 2 == 0

        if blink:
            return

        radius = int(self.radius * 1.8)

        shield_surface = pygame.Surface((radius*2+20, radius*2+20), pygame.SRCALPHA)
        bubble_center = (shield_surface.get_width()//2,
                        shield_surface.get_height()//2)

        # Glow
        for i in range(6, 0, -1):
            pygame.draw.circle(
                shield_surface,
                (180, 220, 255, 25),
                bubble_center,
                radius + i
            )

        # Main bubble
        pygame.draw.circle(
            shield_surface,
            (180, 220, 255, 80),
            bubble_center,
            radius
        )

        # Outline
        pygame.draw.circle(
            shield_surface,
            (255, 255, 255, 140),
            bubble_center,
            radius,
            2
        )

        # Highlight
        pygame.draw.circle(
            shield_surface,
            (255, 255, 255, 60),
            (bubble_center[0] - radius//3,
            bubble_center[1] - radius//3),
            radius//3
        )

        screen.blit(
            shield_surface,
            (center.x - shield_surface.get_width()//2,
            center.y - shield_surface.get_height()//2)
        )

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
        
        if "triple" in self.active_powerups:
            angles = [-10, 0, 10]
            for offset in angles:
                new_rad = math.radians(self.turret_angle + offset - 90)
                new_direction = pygame.Vector2(
                    math.cos(new_rad),
                    math.sin(new_rad),
                )

                new_spawn = self.position + new_direction * barrel_length
                new_bullet = Bullet(new_spawn, new_direction, self)
                self.bullets.append(new_bullet)
        else:
            new_bullet = Bullet(spawn, direction, self)
            self.bullets.append(new_bullet)

        # --- Trigger flash effect and sound ---
        self.flash_timer = self.flash_duration  # Kích hoạt hiệu ứng flash
        
        # --- Muzzle position ---
        # Direction giống đạn (đã có sẵn phía trên)
        # shoot_rad = math.radians(self.turret_angle - 90)
        # direction = pygame.Vector2(
        #     math.cos(shoot_rad),
        #     math.sin(shoot_rad)
        # )

        # # ⭐ TÍNH ĐẦU NÒNG CHUẨN THEO SPRITE
        # muzzle_offset = pygame.Vector2(0, -self.turret_length)
        # muzzle_offset = muzzle_offset.rotate(-self.turret_angle)

        # muzzle_pos = self.position + muzzle_offset
        # # Center tank
        # center = pygame.Vector2(self.position)

        # # Direction giống đạn
        # shoot_rad = math.radians(self.turret_angle - 90)
        # direction = pygame.Vector2(
        #     math.cos(shoot_rad),
        #     math.sin(shoot_rad)
        # )

        # # Chiều dài nòng súng (tùy chỉnh cho khớp sprite)
        # turret_length = 40  # thử 35–50 tùy sprite

        # # muzzle_pos = center + direction * turret_length
        # muzzle_pos = self.muzzle_world_pos # Vị trí đầu nòng đã tính trong render, để đồng bộ chính xác với sprite dù có xoay turret độc lập

        # muzzle_pos = spawn
        # --- Glitter spark effect ---
        for _ in range(8):
            angle_offset = random.uniform(-15, 15)
            speed = random.uniform(120, 220)

            spark_direction = direction.rotate(angle_offset)

            self.sparks.append({
                "pos": pygame.Vector2(spawn),
                "vel": spark_direction * speed,
                "life": 0.4,
                "timer": 0,
                "size": random.randint(3, 6),
                "rot": random.uniform(0, 360),
                "rot_speed": random.uniform(-360, 360)
            })

        self.shoot_sound.play()  # Phát âm thanh bắn

    def take_damage(self):
        if self.shield_active:
            return
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

        # Pickup flash effect (white overlay)
        flash_alpha = 0
        if self.pickup_flash_timer > 0:
            flash_alpha = int(120 * (self.pickup_flash_timer / self.pickup_flash_duration))
        
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

        # --- TURRET ---
        rotated_turret = pygame.transform.rotate(self.turret_image, -self.turret_angle)
        turret_rect = rotated_turret.get_rect(center=center)
        screen.blit(rotated_turret, turret_rect.topleft)

        # Lấy vị trí đầu nòng theo sprite đã rotate
        # muzzle_offset = pygame.Vector2(0, -self.turret_length)
        # muzzle_offset = muzzle_offset.rotate(-self.turret_angle)

        # self.muzzle_world_pos = pygame.Vector2(self.position) + muzzle_offset

        if flash_alpha > 0:
            flash_surface = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(
                flash_surface,
                (255, 255, 255, flash_alpha),
                (flash_surface.get_width()//2,
                flash_surface.get_height()//2),
                self.radius*1.5
            )
            screen.blit(
                flash_surface,
                (center.x - flash_surface.get_width()//2,
                center.y - flash_surface.get_height()//2)
            )

        if self.shield_active:
            self.draw_shield(screen, center)

        # Draw orbit effects
        for effect in self.orbit_effects:
            angle_rad = math.radians(effect["angle"])
            orbit_pos = center + pygame.Vector2(
                math.cos(angle_rad),
                math.sin(angle_rad)
            ) * effect["radius"]

            # 🔵 Lấy màu tank
            base_color = self.color

            # Làm sáng nhẹ cho nổi bật
            bright_color = (
                min(base_color[0] + 40, 255),
                min(base_color[1] + 40, 255),
                min(base_color[2] + 40, 255)
            )

            if effect["type"] == "speed":
                # Mũi tên
                points = [
                    (orbit_pos.x, orbit_pos.y - 7),
                    (orbit_pos.x + 7, orbit_pos.y + 7),
                    (orbit_pos.x - 7, orbit_pos.y + 7)
                ]
                pygame.draw.polygon(screen, bright_color, points)

            elif effect["type"] == "triple":
                # 3 viên đạn mini
                pygame.draw.circle(screen, bright_color,
                                (int(orbit_pos.x), int(orbit_pos.y)), 5)

            # if effect["type"] == "speed":
            #     color = (180, 220, 255)
            #     # vẽ mũi tên
            #     points = [
            #         (orbit_pos.x, orbit_pos.y - 6),
            #         (orbit_pos.x + 6, orbit_pos.y + 6),
            #         (orbit_pos.x - 6, orbit_pos.y + 6)
            #     ]
            #     pygame.draw.polygon(screen, color, points)

            # elif effect["type"] == "triple":
            #     color = (255, 200, 200)
            #     pygame.draw.circle(screen, color,
            #                     (int(orbit_pos.x), int(orbit_pos.y)), 5)

        for spark in self.sparks:
            progress = spark["timer"] / spark["life"]
            alpha = max(0, 255 * (1 - progress))

            size = spark["size"]

            # Làm màu sáng hơn màu tank
            base = self.color
            color = (
                min(base[0] + 80, 255),
                min(base[1] + 80, 255),
                min(base[2] + 80, 255)
            )

            # Tạo surface riêng để xoay + alpha
            sparkle_surface = pygame.Surface((size*3, size*3), pygame.SRCALPHA)

            # Vẽ ngôi sao nhỏ (4 cánh)
            center = size * 1.5
            pygame.draw.line(
                sparkle_surface,
                (*color, int(alpha)),
                (center - size, center),
                (center + size, center),
                2
            )
            pygame.draw.line(
                sparkle_surface,
                (*color, int(alpha)),
                (center, center - size),
                (center, center + size),
                2
            )
            # tiny center glow
            pygame.draw.circle(
                sparkle_surface,
                (255, 255, 255, int(alpha)),
                (int(center), int(center)),
                1
            )

            # Xoay
            rotated = pygame.transform.rotate(sparkle_surface, spark["rot"])
            rect = rotated.get_rect(center=spark["pos"])

            screen.blit(rotated, rect)

            
        
        #     flash_pos = center + pygame.Vector2(math.cos(math.radians(self.angle - 90)),
        #                                         math.sin(math.radians(self.angle - 90))) * (self.radius + 15)
        #     pygame.draw.circle(screen, (255, 255, 0), (int(flash_pos.x), int(flash_pos.y)), 5)

        
        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen, offset)

        # Draw effects
        for effect in self.effects:
            effect.draw(screen, offset)

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