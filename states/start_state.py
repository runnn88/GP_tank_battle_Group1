import pygame
from states.base_state import BaseState
from utils.helpers import draw_text_with_outline

class StartState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.next_state = None  # Biến để lưu trạng thái tiếp theo khi fade xong

        # Fonts for game title and button text
        # self.title_font = pygame.font.SysFont(None, 96)
        self.title_font_big = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96)
        self.title_font_outline = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 110)
        self.title_scale = 1.0  # Scale factor for title animation
        self.pulse_direction = 1  # Direction of pulsing effect (1 for growing, -1 for shrinking)

        # Button font
        self.button_font_small = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 48)  # Font for buttons
        self.button_font_big = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 54)  # Font for buttons
        self.hover_scale = 1.1  # Scale factor for hover effect

        # Background and Sounds
        self.background = pygame.image.load("assets/BG/bgmainmenu.png").convert()
        self.background = pygame.transform.scale(self.background, self.state_machine.screen.get_size())
        self.bg_offset_y = 40  # Độ lệch dọc của background
        self.background = self.background.subsurface((0, 0, self.state_machine.screen.get_width(), self.state_machine.screen.get_height() - self.bg_offset_y - 60))
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.mp3")
        
        # Loop bgm
        # self.bgm = pygame.mixer.Sound("assets/sounds/bgm.mp3")
        # self.bgm.set_volume(0.5)
        # self.bgm.play(-1)  # Loop background music
        pygame.mixer.music.load("assets/sounds/bgm.mp3")
        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(-1)
        self.music_volume = 0

        # Define buttons in the middle of the screen
        screen_rect = self.state_machine.screen.get_rect()
        self.button_scales = {
            "start": 1.0,
            "settings": 1.0,
            "quit": 1.0
        }
        self.button_states = {
            "start": "normal",
            "settings": "normal",
            "quit": "normal"
        }

        # "Press Start" button
        self.button_rect = pygame.Rect(0, 0, 320, 75)
        self.button_rect.center = (screen_rect.centerx, screen_rect.centery + 60)

        # "Settings" button (placed below Start)
        self.setting_button_rect = pygame.Rect(0, 0, 320, 75)
        self.setting_button_rect.center = (screen_rect.centerx, screen_rect.centery + 150)

        # "Quit" button
        self.quit_button_rect = pygame.Rect(0, 0, 320, 75)
        self.quit_button_rect.center = (screen_rect.centerx, screen_rect.centery + 240)

        # Fade transition
        self.is_fading = False
        self.fade_alpha = 0
        self.fade_speed = 400  # tốc độ fade (pixel alpha per second)

        self.fade_surface = pygame.Surface(
            self.state_machine.screen.get_size()
        )
        self.fade_surface.fill((0, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle mouse clicks on buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(event.pos):
                    self.click_sound.play()
                    self.is_fading = True

                if self.button_rect.collidepoint(event.pos):
                    self.button_states["start"] = "pressed"
                    self.click_sound.play()
                    self.is_fading = True
                    self.next_state = "gameplay"

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
        
        if self.music_volume < 0.5:
            self.music_volume += dt * 0.2
            pygame.mixer.music.set_volume(self.music_volume)

        # Lấy vị trí chuột
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
        update_hover(self.setting_button_rect, "settings")
        update_hover(self.quit_button_rect, "quit")
        
        # ===== Fade transition =====
        if self.is_fading:
            self.fade_alpha += self.fade_speed * dt
            # Giảm nhạc khi fade
            current_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(max(0, current_volume - dt))

            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                if self.next_state:
                    self.state_machine.change_state(self.next_state)
                # self.state_machine.change_state("gameplay")

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

        # === Title ===
        center_x = screen.get_rect().centerx
        base_y = screen.get_rect().centery - 200

        # Font động theo scale
        big_size = int(96 * self.title_scale)
        mid_size = int(96 * self.title_scale)
        small_size = int(45 * self.title_scale)

        big_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", big_size)
        mid_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", mid_size)
        small_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", small_size)

        # Render từng dòng
        tank_surface = self.render_outlined_text(
            "TANK",
            big_font,
            (255, 200, 120),  # vàng nhẹ
            (255, 255, 255),
            4
        )

        battle_surface = self.render_outlined_text(
            "BATTLE",
            mid_font,
            (255, 170, 170),  # hồng nhẹ
            (255, 255, 255),
            4
        )

        chaos_surface = self.render_outlined_text(
            "Chaos Maze",
            small_font,
            (53, 56, 92),  # xanh lạnh
            (0, 0, 0),
            2
        )

        # Căn giữa
        tank_rect = tank_surface.get_rect(center=(center_x, base_y))
        battle_rect = battle_surface.get_rect(center=(center_x, base_y + 90))
        chaos_rect = chaos_surface.get_rect(center=(center_x, base_y + 160))

        # Vẽ
        screen.blit(tank_surface, tank_rect)
        screen.blit(battle_surface, battle_rect)
        screen.blit(chaos_surface, chaos_rect)

        def draw_modern_button(rect, text, scale, state):
            scaled_rect = rect.inflate(
                rect.width * (scale - 1),
                rect.height * (scale - 1)
            )

            # ===== MÀU THEO STATE =====
            if state == "pressed":
                bg_color = (80, 160, 255)
                border_color = (255, 255, 255)
                text_color = (20, 30, 50)
            elif state == "hover":
                bg_color = (0, 0, 0, 0)  # trong
                border_color = (120, 200, 255)
                text_color = (220, 240, 255)
            else:
                bg_color = (0, 0, 0, 0)  # trong
                border_color = (100, 150, 200)
                text_color = (180, 210, 240)

            # ===== Glow khi hover =====
            if state == "hover":
                glow = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    glow,
                    (100, 180, 255, 60),
                    glow.get_rect(),
                    border_radius=18
                )
                screen.blit(glow, scaled_rect.topleft)

            # ===== Background (chỉ fill khi pressed) =====
            if state == "pressed":
                pygame.draw.rect(
                    screen,
                    bg_color,
                    scaled_rect,
                    border_radius=18
                )

            # ===== Border =====
            pygame.draw.rect(
                screen,
                border_color,
                scaled_rect,
                3,
                border_radius=18
            )

            # ===== Text =====
            font_size = 54 if scale > 1.01 else 48
            font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", font_size)

            text_surface = self.render_outlined_text(
                text,
                font,
                text_color,
                (0, 0, 0),
                3
            )

            text_rect = text_surface.get_rect(center=scaled_rect.center)
            screen.blit(text_surface, text_rect)

        draw_modern_button(
            self.button_rect,
            "Start",
            self.button_scales["start"],
            self.button_states["start"]
        )

        draw_modern_button(
            self.setting_button_rect,
            "Settings",
            self.button_scales["settings"],
            self.button_states["settings"]
        )

        draw_modern_button(
            self.quit_button_rect,
            "Quit",
            self.button_scales["quit"],
            self.button_states["quit"]
        )

        # Draw fade overlay
        if self.is_fading:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(self.fade_surface, (0, 0))