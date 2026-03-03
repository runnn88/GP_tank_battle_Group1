import pygame


class Wall:
    def __init__(self, x, y, size, image=None, destructible=False, hp=100):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image

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
        
        screen.blit(self.image, draw_rect.topleft)