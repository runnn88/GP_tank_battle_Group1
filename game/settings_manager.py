import pygame
import os
import re


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
        self.fps_cap = 60

        # =========================
        # Feature Toggles
        # =========================
        self.independent_turret = False
        self.destructible_walls = False
        self.powerups_enabled = False
        self.bullet_can_hit_self = False

        # =========================
        # Audio
        # =========================
        self.master_volume = 0.5  # 0.0 -> 1.0
        self._registered_sounds = []

        # Map
        self.random_map = False
        self.map_width = 16
        self.map_height = 12
        self.allow_destructible = True
        self.allow_indestructible = True
        self.wall_density = 0.25
        self.level_paths = []
        self.current_level_index = 0
        self.refresh_levels()

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

    def apply_audio_settings(self):
        pygame.mixer.music.set_volume(self.master_volume)

        alive_sounds = []
        for sound in self._registered_sounds:
            if sound is None:
                continue
            sound.set_volume(self.master_volume)
            alive_sounds.append(sound)
        self._registered_sounds = alive_sounds

    def register_sound(self, sound):
        if sound is None:
            return
        self._registered_sounds.append(sound)
        sound.set_volume(self.master_volume)

    def refresh_levels(self):
        maps_dir = os.path.join("data", "maps")
        level_files = []

        if os.path.isdir(maps_dir):
            for name in os.listdir(maps_dir):
                if not name.lower().endswith(".txt"):
                    continue
                full_path = os.path.join(maps_dir, name)
                if os.path.isfile(full_path):
                    level_files.append(full_path)

        def level_sort_key(path):
            base = os.path.basename(path).lower()
            match = re.search(r"(\d+)", base)
            number = int(match.group(1)) if match else 10_000
            return (number, base)

        level_files.sort(key=level_sort_key)
        self.level_paths = level_files

        if self.level_paths:
            self.current_level_index %= len(self.level_paths)
        else:
            self.current_level_index = 0

    @property
    def selected_level_path(self):
        if not self.level_paths:
            self.refresh_levels()
        if self.level_paths:
            return self.level_paths[self.current_level_index]
        return os.path.join("data", "maps", "level1.txt")

    @property
    def selected_level_label(self):
        name = os.path.basename(self.selected_level_path)
        stem, _ = os.path.splitext(name)
        return stem.upper()

    def cycle_level(self, step=1):
        if not self.level_paths:
            self.refresh_levels()
        if not self.level_paths:
            return
        self.current_level_index = (self.current_level_index + step) % len(self.level_paths)


settings = Settings()
