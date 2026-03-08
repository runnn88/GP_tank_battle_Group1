import pygame
import random
import math

class PowerUp:
    SIZE = 40
    BUBBLE_RADIUS = 30
    TYPES = ["speed", "shield", "triple"]
    COLORS = {
        "speed": (180, 220, 255),     # pastel blue
        "shield": (220, 180, 255),    # pastel purple
        "triple": (255, 200, 200)     # pastel pink
    }

    def __init__(self, position):
        self.type = random.choice(self.TYPES)
        self.base_position = pygame.Vector2(position)
        self.position = pygame.Vector2(position)
        
        self.rect = pygame.Rect(
            self.position.x - self.SIZE//2,
            self.position.y - self.SIZE//2,
            self.SIZE,
            self.SIZE
        )

        if not hasattr(PowerUp, "IMAGES"):
            PowerUp._load_images()

        self.duration = 5.0
        self.lifetime = 10.0  # tồn tại 10s nếu không ai nhặt
        self.timer = 0

        # Animation
        self.float_timer = random.uniform(0, 2 * math.pi)

    @classmethod
    def _load_images(cls):
        speed = pygame.image.load("assets/image/speed1.png").convert_alpha()
        shield = pygame.image.load("assets/image/shield1.png").convert_alpha()
        triple = pygame.image.load("assets/image/trip1.png").convert_alpha()

        cls.IMAGES = {
            "speed": pygame.transform.scale(speed, (cls.SIZE, cls.SIZE)),
            "shield": pygame.transform.scale(shield, (cls.SIZE, cls.SIZE)),
            "triple": pygame.transform.scale(triple, (cls.SIZE, cls.SIZE))
        }

    def update(self, dt):
        self.timer += dt
        self.float_timer += dt * 2

        # Float lên xuống
        float_offset = math.sin(self.float_timer) * 6
        self.position.y = self.base_position.y + float_offset

        self.rect.center = self.position

    def render(self, screen, offset):
        center_x = int(self.position.x + offset.x)
        center_y = int(self.position.y + offset.y)

        bubble_surface = pygame.Surface((90, 90), pygame.SRCALPHA)

        radius = self.BUBBLE_RADIUS
        bubble_center = (45, 45)

        # --- Glow mềm bên ngoài ---
        for i in range(6, 0, -1):
            alpha = 20
            glow_color = (*self.COLORS[self.type], alpha)
            pygame.draw.circle(
                bubble_surface,
                glow_color,
                bubble_center,
                radius + i
            )

        # --- Lớp bong bóng chính ---
        bubble_color = (*self.COLORS[self.type], 90)
        pygame.draw.circle(
            bubble_surface,
            bubble_color,
            bubble_center,
            radius
        )

        # --- Viền trắng mỏng ---
        pygame.draw.circle(
            bubble_surface,
            (255, 255, 255, 160),
            bubble_center,
            radius,
            2
        )

        # --- Highlight bóng (quan trọng) ---
        highlight_surface = pygame.Surface((90, 90), pygame.SRCALPHA)
        pygame.draw.circle(
            highlight_surface,
            (255, 255, 255, 80),
            (35, 32),   # lệch lên trái
            12
        )
        pygame.draw.circle(
            highlight_surface,
            (255, 255, 255, 40),
            (30, 28),
            18,
            2
        )

        bubble_surface.blit(highlight_surface, (0, 0))

        screen.blit(bubble_surface, (center_x - 45, center_y - 45))

        # --- Icon ---
        image = self.IMAGES[self.type]
        icon_rect = image.get_rect(center=(center_x, center_y))
        screen.blit(image, icon_rect)

    def collides_with_circle(self, center, radius):
        total_radius = self.BUBBLE_RADIUS + radius
        return self.position.distance_squared_to(center) <= (total_radius * total_radius)

    # def render(self, screen, offset):
    #     center_x = int(self.position.x + offset.x)
    #     center_y = int(self.position.y + offset.y)

    #     # --------- Bubble Layer ----------
    #     bubble_surface = pygame.Surface((80, 80), pygame.SRCALPHA)

    #     # Pulse scale
    #     pulse = 1 + 0.05 * math.sin(self.float_timer * 2)

    #     radius = int(28 * pulse)

    #     # Glow vòng ngoài
    #     glow_color = (*self.COLORS[self.type], 60)
    #     pygame.draw.circle(bubble_surface, glow_color, (40, 40), radius + 6)

    #     # Vòng chính trong suốt
    #     bubble_color = (*self.COLORS[self.type], 100)
    #     pygame.draw.circle(bubble_surface, bubble_color, (40, 40), radius)

    #     # Viền trắng mềm
    #     pygame.draw.circle(bubble_surface, (255, 255, 255, 120), (40, 40), radius, 2)

    #     screen.blit(bubble_surface, (center_x - 40, center_y - 40))

    #     # --------- Icon ----------
    #     image = self.IMAGES[self.type]
    #     icon_rect = image.get_rect(center=(center_x, center_y))
    #     screen.blit(image, icon_rect)


        # image = self.IMAGES[self.type]
        # draw_rect = image.get_rect(
        #     center=(int(self.position.x + offset.x), 
        #             int(self.position.y + offset.y)))
        # screen.blit(image, draw_rect)
        # color = self.COLORS[self.type]
        # pygame.draw.circle(
        #     screen,
        #     color,
        #     (int(self.position.x + offset.x),
        #      int(self.position.y + offset.y)),
        #     self.SIZE//2
        # )

    def is_expired(self):
        return self.timer >= self.lifetime
