import pygame
from states.base_state import BaseState
from utils.helpers import draw_text_with_outline
from game.settings_manager import settings


class StartState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.next_state = None

        self.title_font_big = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96)
        self.title_font_outline = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 110)
        self.title_scale = 1.0
        self.pulse_direction = 1

        self.button_font_small = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 48)
        self.button_font_big = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 54)
        self.hover_scale = 1.1

        self.background_source = pygame.image.load("assets/BG/bgmainmenu.png").convert()
        self.background = pygame.transform.scale(self.background_source, self.state_machine.screen.get_size())
        self.bg_offset_y = 40
        bg_h = max(1, self.state_machine.screen.get_height() - self.bg_offset_y - 60)
        self.background = self.background.subsurface((0, 0, self.state_machine.screen.get_width(), bg_h))

        self.click_sound = pygame.mixer.Sound("assets/sounds/click.mp3")
        settings.register_sound(self.click_sound)

        pygame.mixer.music.load("assets/sounds/bgm.mp3")
        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(-1)
        self.music_volume = 0

        screen_rect = self.state_machine.screen.get_rect()
        self.button_scales = {
            "start": 1.0,
            "levels": 1.0,
            "settings": 1.0,
            "quit": 1.0,
        }
        self.button_states = {
            "start": "normal",
            "levels": "normal",
            "settings": "normal",
            "quit": "normal",
        }

        self.button_rect = pygame.Rect(0, 0, 320, 75)
        self.levels_button_rect = pygame.Rect(0, 0, 320, 75)
        self.setting_button_rect = pygame.Rect(0, 0, 320, 75)
        self.quit_button_rect = pygame.Rect(0, 0, 320, 75)
        self._layout_buttons(screen_rect)

        self.is_fading = False
        self.fade_alpha = 0
        self.fade_speed = 400

        self.fade_surface = pygame.Surface(self.state_machine.screen.get_size())
        self.fade_surface.fill((0, 0, 0))

    def on_resume(self):
        self.button_scales = {key: 1.0 for key in self.button_scales}
        self.button_states = {key: "normal" for key in self.button_states}
        self.is_fading = False
        self.next_state = None
        self.fade_alpha = 0
        self.music_volume = pygame.mixer.music.get_volume()

    def on_resize(self, screen):
        scaled = pygame.transform.scale(self.background_source, screen.get_size())
        bg_h = max(1, screen.get_height() - self.bg_offset_y - 60)
        self.background = scaled.subsurface((0, 0, screen.get_width(), bg_h))

        self._layout_buttons(screen.get_rect())

        self.fade_surface = pygame.Surface(screen.get_size())
        self.fade_surface.fill((0, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(event.pos):
                    self.button_states["start"] = "pressed"
                    self.click_sound.play()
                    self.is_fading = True
                    self.next_state = "gameplay"

                elif self.levels_button_rect.collidepoint(event.pos):
                    self.button_states["levels"] = "pressed"
                    self.click_sound.play()
                    self.is_fading = True
                    self.next_state = "level_select"

                elif self.setting_button_rect.collidepoint(event.pos):
                    self.button_states["settings"] = "pressed"
                    self.click_sound.play()
                    self.is_fading = True
                    self.next_state = "settings"

                elif self.quit_button_rect.collidepoint(event.pos):
                    self.button_states["quit"] = "pressed"
                    self.click_sound.play()
                    return False

        return True

    def update(self, dt):
        self.title_scale += self.pulse_direction * dt * 0.5
        if self.title_scale > 1.05:
            self.pulse_direction = -1
        elif self.title_scale < 0.95:
            self.pulse_direction = 1

        target_volume = settings.master_volume
        if self.music_volume < target_volume:
            self.music_volume = min(target_volume, self.music_volume + dt * 0.2)
        elif self.music_volume > target_volume:
            self.music_volume = max(target_volume, self.music_volume - dt * 0.4)
        pygame.mixer.music.set_volume(self.music_volume)

        mouse_pos = pygame.mouse.get_pos()

        def update_hover(rect, key):
            if rect.collidepoint(mouse_pos):
                if self.button_states[key] != "pressed":
                    self.button_states[key] = "hover"
                self.button_scales[key] = min(self.button_scales[key] + dt * 6, 1.08)
            else:
                if self.button_states[key] != "pressed":
                    self.button_states[key] = "normal"
                self.button_scales[key] = max(self.button_scales[key] - dt * 6, 1.0)

        update_hover(self.button_rect, "start")
        update_hover(self.levels_button_rect, "levels")
        update_hover(self.setting_button_rect, "settings")
        update_hover(self.quit_button_rect, "quit")

        if self.is_fading:
            self.fade_alpha += self.fade_speed * dt
            current_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(max(0, current_volume - dt))

            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                if self.next_state:
                    next_state = self.next_state
                    self.is_fading = False
                    self.next_state = None
                    self.fade_alpha = 0
                    self.state_machine.change_state(next_state, previous_state=self)

    def render_outlined_text(self, text, font, text_color, outline_color, outline_width):
        outline_surface = font.render(text, True, outline_color)
        w = outline_surface.get_width() + 2 * outline_width
        h = outline_surface.get_height() + 2 * outline_width

        text_surface = pygame.Surface((w, h), pygame.SRCALPHA)

        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    text_surface.blit(outline_surface, (dx + outline_width, dy + outline_width))

        inner_text = font.render(text, True, text_color)
        text_surface.blit(inner_text, (outline_width, outline_width))

        return text_surface

    def render(self, screen):
        screen.fill((20, 20, 20))
        screen.blit(self.background, (0, self.bg_offset_y))

        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        center_x = screen.get_rect().centerx
        screen_h = screen.get_height()

        big_size = max(64, min(int(96 * self.title_scale), int(screen_h * 0.16)))
        mid_size = max(64, min(int(96 * self.title_scale), int(screen_h * 0.16)))
        small_size = max(28, min(int(45 * self.title_scale), int(screen_h * 0.075)))

        big_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", big_size)
        mid_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", mid_size)
        small_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", small_size)

        tank_surface = self.render_outlined_text("TANK", big_font, (255, 200, 120), (255, 255, 255), 4)
        battle_surface = self.render_outlined_text("BATTLE", mid_font, (255, 170, 170), (255, 255, 255), 4)
        chaos_surface = self.render_outlined_text("Chaos Maze", small_font, (53, 56, 92), (0, 0, 0), 2)

        title_top = int(screen_h * 0.10)
        gap = 8
        tank_rect = tank_surface.get_rect(midtop=(center_x, title_top))
        battle_rect = battle_surface.get_rect(midtop=(center_x, tank_rect.bottom + gap))
        chaos_rect = chaos_surface.get_rect(midtop=(center_x, battle_rect.bottom + gap))

        screen.blit(tank_surface, tank_rect)
        screen.blit(battle_surface, battle_rect)
        screen.blit(chaos_surface, chaos_rect)

        def draw_modern_button(rect, text, scale, state):
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))

            if state == "pressed":
                bg_color = (80, 160, 255)
                border_color = (255, 255, 255)
                text_color = (20, 30, 50)
            elif state == "hover":
                bg_color = (0, 0, 0, 0)
                border_color = (120, 200, 255)
                text_color = (220, 240, 255)
            else:
                bg_color = (0, 0, 0, 0)
                border_color = (100, 150, 200)
                text_color = (180, 210, 240)

            if state == "hover":
                glow = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(glow, (100, 180, 255, 60), glow.get_rect(), border_radius=18)
                screen.blit(glow, scaled_rect.topleft)

            if state == "pressed":
                pygame.draw.rect(screen, bg_color, scaled_rect, border_radius=18)

            pygame.draw.rect(screen, border_color, scaled_rect, 3, border_radius=18)

            base_size = int(rect.height * 0.62)
            font_size = min(54, base_size + (4 if scale > 1.01 else 0))
            min_size = 24
            while True:
                font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", font_size)
                text_surface = self.render_outlined_text(text, font, text_color, (0, 0, 0), 3)
                if text_surface.get_width() <= scaled_rect.width - 20 or font_size <= min_size:
                    break
                font_size -= 2

            text_rect = text_surface.get_rect(center=scaled_rect.center)
            screen.blit(text_surface, text_rect)

        draw_modern_button(self.button_rect, "Start", self.button_scales["start"], self.button_states["start"])
        draw_modern_button(self.levels_button_rect, "Levels", self.button_scales["levels"], self.button_states["levels"])
        draw_modern_button(self.setting_button_rect, "Settings", self.button_scales["settings"], self.button_states["settings"])
        draw_modern_button(self.quit_button_rect, "Quit", self.button_scales["quit"], self.button_states["quit"])

        if self.is_fading:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(self.fade_surface, (0, 0))

    def _layout_buttons(self, screen_rect):
        count = 4
        top_reserved = int(screen_rect.height * 0.50)
        bottom_margin = 20
        gap = 16

        available = max(240, screen_rect.height - top_reserved - bottom_margin)
        button_h = max(52, min(75, (available - gap * (count - 1)) // count))
        button_w = max(240, min(360, screen_rect.width - 80))

        self.button_rect.size = (button_w, button_h)
        self.levels_button_rect.size = (button_w, button_h)
        self.setting_button_rect.size = (button_w, button_h)
        self.quit_button_rect.size = (button_w, button_h)

        total_h = count * button_h + (count - 1) * gap
        min_top = top_reserved
        max_top = max(min_top, screen_rect.height - total_h - bottom_margin)
        desired_top = int(screen_rect.height * 0.70 - total_h / 2)
        top = max(min_top, min(desired_top, max_top))

        centers = [top + button_h // 2 + i * (button_h + gap) for i in range(count)]
        self.button_rect.center = (screen_rect.centerx, centers[0])
        self.levels_button_rect.center = (screen_rect.centerx, centers[1])
        self.setting_button_rect.center = (screen_rect.centerx, centers[2])
        self.quit_button_rect.center = (screen_rect.centerx, centers[3])