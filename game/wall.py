import pygame


class Wall:
    def __init__(self, x, y, size, image=None, destructible=False, hp=100):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.destructible_image = pygame.image.load("assets/destructible_wall.png").convert_alpha() if destructible else None

        # Extension features
        self.destructible = destructible
        self.max_hp = hp if destructible else -1
        self.hp = self.max_hp

    def take_damage(self):
        if not self.destructible:
            return False
        
        self.hp -= 25  # Example damage value

        if self.hp <= 0:
            return True
        
        return False
    
    def render(self, screen, offset=pygame.Vector2(0, 0)):
        draw_rect = self.rect.move(offset.x, offset.y)
        
        if self.destructible and self.destructible_image:
            screen.blit(self.destructible_image, draw_rect.topleft)
        else:
            if self.image:
                screen.blit(self.image, draw_rect.topleft)
            else:
                pygame.draw.rect(screen, (100, 100, 100), draw_rect)