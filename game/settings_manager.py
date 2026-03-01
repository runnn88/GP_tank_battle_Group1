import pygame


class Settings:
    def __init__(self):

        # =========================
        # Window Settings
        # =========================
        self.windowed_resolutions = [
            (1000, 700),
            (1280, 720),
            (1600, 900),
            (1920, 1080),
        ]

        self.current_resolution_index = 0
        self.fullscreen = False

        # =========================
        # Feature Toggles
        # =========================
        self.independent_turret = False
        self.destructible_walls = False
        self.powerups_enabled = False
        self.bullet_can_hit_self = False
        
        # Map
        self.random_map = False
        self.map_width = 16
        self.map_height = 12
        self.allow_destructible = True
        self.allow_indestructible = True
        self.wall_density = 0.25

        # Gameplay
        self.max_bounces = 3
        self.friendly_fire = False

        # Keybinds
        self.keybinds = {
            "p1_turret_left": pygame.K_r,
            "p1_turret_right": pygame.K_t,
            "p2_turret_left": pygame.K_n,
            "p2_turret_right": pygame.K_m,
        }

    @property
    def resolution(self):
        return self.windowed_resolutions[self.current_resolution_index]


settings = Settings()