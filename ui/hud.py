import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, UI_SIDE_WIDTH, MAX_BULLETS, TOP_UI_HEIGHT


class HUD:
    def __init__(self):
        # For nicer typography, prefer a bundled TTF if you add one later:
        # e.g. put a file at assets/ui_font.ttf and it will be used automatically.
        try:
            self.font = pygame.font.Font("assets/ui_font.ttf", 22)
            self.title_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 30)
            self.section_font = pygame.font.Font("assets/ui_font.ttf", 20)
        except Exception:
            # Windows-friendly defaults
            self.font = pygame.font.SysFont("bahnschrift", 22)
            self.title_font = pygame.font.SysFont("bahnschrift", 30, bold=True)
            self.section_font = pygame.font.SysFont("segoeui", 20)

        self.time_left = 120.0  # Example timer for the top banner

    def _draw_missile(self, screen, center, active=True):
        """Draw a small missile icon (no image asset needed)."""
        x, y = int(center[0]), int(center[1])
        if active:
            body = (235, 235, 70)
            outline = (30, 30, 30)
            tip = (255, 170, 50)
        else:
            body = (85, 85, 90)
            outline = (25, 25, 28)
            tip = (120, 120, 130)

        # Body
        w, h = 12, 6
        body_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(screen, body, body_rect, border_radius=2)
        pygame.draw.rect(screen, outline, body_rect, 1, border_radius=2)

        # Nose cone (pointing right)
        nose = [(x + w // 2, y), (x + w // 2 - 4, y - 4), (x + w // 2 - 4, y + 4)]
        pygame.draw.polygon(screen, tip, nose)
        pygame.draw.polygon(screen, outline, nose, 1)

        # Fins
        fin1 = [(x - w // 2 + 2, y - h // 2), (x - w // 2 - 2, y - h // 2 - 3), (x - w // 2 + 3, y - h // 2)]
        fin2 = [(x - w // 2 + 2, y + h // 2), (x - w // 2 - 2, y + h // 2 + 3), (x - w // 2 + 3, y + h // 2)]
        pygame.draw.polygon(screen, body, fin1)
        pygame.draw.polygon(screen, body, fin2)
        pygame.draw.polygon(screen, outline, fin1, 1)
        pygame.draw.polygon(screen, outline, fin2, 1)

    def draw_bullet_icon(self, surface, center, active=True):
        x, y = center

        if active:
            color = (255, 220, 120)
        else:
            color = (210, 210, 220)

        pygame.draw.circle(surface, color, (x, y), 8)
        pygame.draw.circle(surface, (255, 255, 255), (x - 3, y - 3), 3)

    def update(self, dt):
        if self.time_left > 0:
            self.time_left -= dt
            if self.time_left < 0:
                self.time_left = 0
    
    def render(self, screen, p1, p2):      
        def draw_glass_panel(surface, rect, border_color):
            glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            # glass.fill((255, 255, 255, 180))  # trắng trong

            pygame.draw.rect(
                glass,
                (255, 255, 255, 130),
                glass.get_rect(),
                border_radius=20
            )

            # Vẽ border
            pygame.draw.rect(
                glass,
                border_color,
                glass.get_rect(),
                3,
                border_radius=20
            )

            surface.blit(glass, rect.topleft)
        
        def draw_trapezoid_timer(surface, center_x, top_y, width, height, color):
            top_width = width
            bottom_width = int(width * 0.6)

            x1 = center_x - top_width // 2
            x2 = center_x + top_width // 2

            xb1 = center_x - bottom_width // 2
            xb2 = center_x + bottom_width // 2

            points = [
                (x1, top_y),
                (x2, top_y),
                (xb2, top_y + height),
                (xb1, top_y + height)
            ]

            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (120, 180, 255), points, 3)
        
        def draw_health_bar(surface, x, y, width, height, health_ratio, base_color):
            bg_rect = pygame.Rect(x, y, width, height)

            # nền pastel nhạt
            pygame.draw.rect(surface, (230, 230, 240), bg_rect, border_radius=height)

            fill_width = int(width * health_ratio)
            fill_rect = pygame.Rect(x, y, fill_width, height)

            pygame.draw.rect(surface, base_color, fill_rect, border_radius=height)

            # highlight bóng dễ thương
            highlight = pygame.Rect(x, y, fill_width, height // 2)
            pygame.draw.rect(surface, (255, 255, 255), highlight, border_radius=height)

        def draw_ammo_icons(surface, start_x, y, current_ammo, max_ammo, align_right=False):
            import random
            spacing = 22

            for i in range(max_ammo):
                if align_right:
                    cx = start_x - i * spacing
                else:
                    cx = start_x + i * spacing

                active = i < current_ammo

                # Nếu hết đạn → rung nhẹ
                if current_ammo == 0:
                    cx += random.randint(-2, 2)

                self.draw_bullet_icon(surface, (cx, y), active)
        
        def draw_name_badge(surface, text, rect, align_left=True, color=(120,220,180)):
            badge_height = 28
            badge_width = 140

            if align_left:
                badge_rect = pygame.Rect(rect.x + 15, rect.y + 10, badge_width, badge_height)
            else:
                badge_rect = pygame.Rect(rect.right - badge_width - 15, rect.y + 10, badge_width, badge_height)

            # nền badge
            pygame.draw.rect(surface, color, badge_rect, border_radius=14)

            # chữ
            label = self.section_font.render(text, True, (255,255,255))
            label_rect = label.get_rect(center=badge_rect.center)
            surface.blit(label, label_rect)
        
        
        font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 22)
        big_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 36)


        # PLAYER 1
        p1_rect = pygame.Rect(20, 15, 320, 80)
        draw_glass_panel(screen, p1_rect, (150, 200, 255))
        
        # name_text = font.render("P1", True, (150, 200, 255))
        # name_rect = name_text.get_rect(topleft=(p1_rect.x + 20, p1_rect.y - 5))
        # screen.blit(name_text, name_rect)
        
        # draw_name_badge(screen, "🌱 PLAYER 1", p1_rect, align_left=True, color=(120,220,180))
        draw_health_bar(screen, 
                        p1_rect.x + 20, 
                        p1_rect.y + 15, 
                        250, 
                        20,
                        p1.health / p1.max_health,
                        base_color=(150, 200, 255))

        ammo_y = p1_rect.y + 55
        draw_ammo_icons(screen,
                        p1_rect.x + 30,
                        ammo_y,
                        MAX_BULLETS - len(p1.bullets),
                        MAX_BULLETS,
                        align_right=False)

        # PLAYER 2
        p2_rect = pygame.Rect(SCREEN_WIDTH - 340, 15, 320, 80)
        draw_glass_panel(screen, p2_rect, (255, 170, 200))
        
        # draw_name_badge(screen, "🌸 PLAYER 2", p2_rect, align_left=False, color=(255,170,200))

        draw_health_bar(screen,
                        p2_rect.right - 270,
                        p2_rect.y + 15,
                        250,
                        20,
                        p2.health / p2.max_health,
                        base_color=(255, 100, 120))

        ammo_y = p2_rect.y + 55
        draw_ammo_icons(screen,
                        p2_rect.right - 30,
                        ammo_y,
                        MAX_BULLETS - len(p2.bullets),
                        MAX_BULLETS,
                        align_right=True)
    
    
        timer_rect = pygame.Rect(0, 0, 140, 60)
        timer_rect.center = (SCREEN_WIDTH // 2, 40)

        pygame.draw.rect(screen, (255, 255, 255), timer_rect, border_radius=30)
        pygame.draw.rect(screen, (200, 170, 255), timer_rect, 3, border_radius=30)

        time_color = (200, 170, 255)

        if self.time_left <= 10:
            time_color = (255, 90, 90)

        time_text = big_font.render(f"{int(self.time_left)}", True, time_color)
        screen.blit(time_text, time_text.get_rect(center=timer_rect.center))
    