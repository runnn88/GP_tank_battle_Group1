import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, UI_SIDE_WIDTH, MAX_BULLETS


class HUD:
    def __init__(self):
        # For nicer typography, prefer a bundled TTF if you add one later:
        # e.g. put a file at assets/ui_font.ttf and it will be used automatically.
        try:
            self.font = pygame.font.Font("assets/ui_font.ttf", 22)
            self.title_font = pygame.font.Font("assets/ui_font.ttf", 30)
            self.section_font = pygame.font.Font("assets/ui_font.ttf", 20)
        except Exception:
            # Windows-friendly defaults
            self.font = pygame.font.SysFont("bahnschrift", 22)
            self.title_font = pygame.font.SysFont("bahnschrift", 30, bold=True)
            self.section_font = pygame.font.SysFont("segoeui", 20)

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

    def render_player_panel(self, screen, player, is_left=True):
        panel_rect = pygame.Rect(
            0 if is_left else SCREEN_WIDTH - UI_SIDE_WIDTH,
            0,
            UI_SIDE_WIDTH,
            SCREEN_HEIGHT,
        )

        # Background frame
        bg_color = (12, 12, 16)
        border_color = (70, 70, 90)
        inner_color = (20, 20, 28)
        pygame.draw.rect(screen, bg_color, panel_rect)
        pygame.draw.rect(screen, border_color, panel_rect, 3)

        inner_rect = panel_rect.inflate(-12, -12)
        pygame.draw.rect(screen, inner_color, inner_rect, border_radius=10)

        # Title (Player 1 / Player 2)
        title_text = "Player 1" if is_left else "Player 2"
        title_color = (0, 220, 120) if is_left else (255, 80, 80)
        title_surf = self.title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(inner_rect.centerx, inner_rect.top + 30))
        screen.blit(title_surf, title_rect)

        # HP bar
        bullets_left = MAX_BULLETS - len(player.bullets)
        cooldown = getattr(player, "shoot_cooldown", 0.0)

        max_hp = 100
        hp_ratio = max(0.0, min(1.0, player.health / max_hp))

        bar_width = inner_rect.width - 40
        bar_height = 16
        bar_x = inner_rect.left + 20
        bar_y = inner_rect.top + 72

        bg_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fg_bar_rect = pygame.Rect(bar_x, bar_y, int(bar_width * hp_ratio), bar_height)

        pygame.draw.rect(screen, (60, 25, 25), bg_bar_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 220, 100), fg_bar_rect, border_radius=6)

        hp_text = self.section_font.render(
            f"HP: {player.health}/{max_hp}", True, (230, 230, 230)
        )
        # More spacing between label and bar
        hp_rect = hp_text.get_rect(midleft=(bar_x, bar_y - 14))
        screen.blit(hp_text, hp_rect)

        # Bullets icons
        bullet_y = bar_y + 52
        label = self.section_font.render("Bullets", True, (200, 200, 200))
        label_rect = label.get_rect(midleft=(bar_x, bullet_y - 12))
        screen.blit(label, label_rect)

        spacing = 18
        start_x = bar_x
        for i in range(MAX_BULLETS):
            cx = start_x + i * spacing + 6
            cy = bullet_y + 10
            self._draw_missile(screen, (cx, cy), active=i < bullets_left)

        # Cooldown bar
        cd_y = bullet_y + 54
        cd_label = self.section_font.render("Cooldown", True, (200, 200, 200))
        cd_label_rect = cd_label.get_rect(midleft=(bar_x, cd_y - 12))
        screen.blit(cd_label, cd_label_rect)

        cd_bar_width = bar_width
        cd_bar_height = 10
        cd_bg = pygame.Rect(bar_x, cd_y, cd_bar_width, cd_bar_height)
        pygame.draw.rect(screen, (35, 35, 45), cd_bg, border_radius=5)

        # cooldown ratio: 1 when just fired, 0 when ready
        cd_max = 0.4
        cd_ratio = max(0.0, min(1.0, cooldown / cd_max))
        if cd_ratio > 0:
            cd_fg = pygame.Rect(bar_x, cd_y, int(cd_bar_width * cd_ratio), cd_bar_height)
            pygame.draw.rect(screen, (120, 180, 255), cd_fg, border_radius=5)

    def render(self, screen, p1, p2):
        # Left panel for Player 1, right panel for Player 2
        self.render_player_panel(screen, p1, is_left=True)
        self.render_player_panel(screen, p2, is_left=False)