import pygame


class Wall:
    def __init__(self, x, y, size, destructible=False, hp=3):
        self.rect = pygame.Rect(x, y, size, size)

        # Extension features
        self.destructible = destructible
        self.max_hp = hp if destructible else -1
        self.hp = self.max_hp

    # ==========================================
    # DAMAGE SYSTEM
    # ==========================================
    def take_damage(self):
        if not self.destructible:
            return False

        self.hp -= 1

        if self.hp <= 0:
            return True  # signal wall should be removed

        return False

    # ==========================================
    # RENDER 
    # ==========================================
    def render(self, screen, offset=pygame.Vector2(0, 0)):
        draw_rect = self.rect.move(offset.x, offset.y)

        # Color logic
        if self.destructible:
            # Change color based on remaining HP
            health_ratio = self.hp / self.max_hp
            color = (
                int(160 * health_ratio),
                int(82 * health_ratio),
                int(45 * health_ratio),
            )
        else:
            color = (100, 100, 100)

        pygame.draw.rect(screen, color, draw_rect)