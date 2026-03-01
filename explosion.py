# explosion.py
import pygame

class Explosion:
    def __init__(self, position, duration=1.0, max_size=60):
        """
        Hiệu ứng nổ.
        :param position: Vị trí nổ (pygame.Vector2).
        :param duration: Thời gian tồn tại của hiệu ứng nổ (giây).
        :param max_size: Kích thước tối đa của hiệu ứng nổ.
        """
        self.position = pygame.Vector2(position)
        self.duration = duration
        self.max_size = max_size
        self.timer = 0.0  # Thời gian đã trôi qua
        self.alive = True  # Hiệu ứng còn tồn tại

    def update(self, dt):
        """
        Cập nhật trạng thái hiệu ứng nổ.
        :param dt: Delta time (thời gian giữa các khung hình).
        """
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False  # Hiệu ứng kết thúc

    def render(self, screen):
        """
        Vẽ hiệu ứng nổ lên màn hình.
        :param screen: Màn hình pygame.
        """
        if not self.alive:
            return

        # Tính toán kích thước và độ trong suốt dựa trên thời gian
        progress = self.timer / self.duration
        size = int(self.max_size * progress)
        alpha = max(255 - int(255 * progress), 0)

        # Tạo surface để vẽ hiệu ứng nổ
        explosion_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            explosion_surface,
            (255, 100, 0, alpha),  # Màu cam với độ trong suốt
            (size, size),
            size,
        )
        screen.blit(explosion_surface, (self.position.x - size, self.position.y - size))