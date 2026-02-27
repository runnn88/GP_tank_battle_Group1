import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, UI_SIDE_WIDTH, MAX_BULLETS


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 32)

    def render_player_panel(self, screen, player, is_left=True):
        panel_rect = pygame.Rect(
            0 if is_left else SCREEN_WIDTH - UI_SIDE_WIDTH,
            0,
            UI_SIDE_WIDTH,
            SCREEN_HEIGHT,
        )

        # Background
        bg_color = (25, 25, 25)
        border_color = (80, 80, 80)
        pygame.draw.rect(screen, bg_color, panel_rect)
        pygame.draw.rect(screen, border_color, panel_rect, 2)

        # Title (Player 1 / Player 2)
        title_text = "Player 1" if is_left else "Player 2"
        title_color = (0, 220, 0) if is_left else (220, 0, 0)
        title_surf = self.title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(panel_rect.centerx, 40))
        screen.blit(title_surf, title_rect)

        # Stats
        bullets_left = MAX_BULLETS - len(player.bullets)
        cooldown = getattr(player, "shoot_cooldown", 0.0)

        lines = [
            f"HP: {player.health}",
            f"Bullets: {bullets_left}",
            f"CD: {cooldown:.1f}s",
        ]

        y = 90
        for line in lines:
            surf = self.font.render(line, True, (220, 220, 220))
            rect = surf.get_rect(center=(panel_rect.centerx, y))
            screen.blit(surf, rect)
            y += 32

    def render(self, screen, p1, p2):
        # Left panel for Player 1, right panel for Player 2
        self.render_player_panel(screen, p1, is_left=True)
        self.render_player_panel(screen, p2, is_left=False)