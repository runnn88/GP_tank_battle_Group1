import pygame
from states.base_state import BaseState
from game.settings_manager import settings
from utils.display_manager import apply_display_settings


class SettingsState(BaseState):
    def __init__(self, state_machine, previous_state=None):
        super().__init__(state_machine)
        self.tab_rects = []
        self.option_rects = []

        self.previous_state = previous_state

        self.tab = 0  # 0 = Settings, 1 = Keybinds
        self.selected = 0
        self.waiting_for_key = None

        self.tabs = ["SETTINGS", "KEYBINDS"]
        self.dragging_volume = False

        self.game_options = [
            "Independent Turret",
            "Bullet Can Hit Self",
            "Resolution",
            "Fullscreen",
            "Master Volume"
        ]

        self.keybind_options = [
            "P1 Turret Left",
            "P1 Turret Right",
            "P2 Turret Left",
            "P2 Turret Right"
        ]

    # =========================================================
    # EVENTS
    # =========================================================

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if self.waiting_for_key:
                    settings.keybinds[self.waiting_for_key] = event.key
                    self.waiting_for_key = None
                    return True

                if event.key == pygame.K_LEFT:
                    self.switch_tab(-1)

                if event.key == pygame.K_RIGHT:
                    self.switch_tab(1)

                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % self.option_count()

                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % self.option_count()

                if event.key == pygame.K_RETURN:
                    self.activate_option()

                if event.key == pygame.K_ESCAPE:
                    self.state_machine.current_state = self.previous_state

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # self.handle_mouse_click(pygame.mouse.get_pos())
                mouse_pos = pygame.mouse.get_pos()

                # Check volume slider drag
                if self.tab == 0 and self.selected == 4:
                    self.dragging_volume = True

                self.handle_mouse_click(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_volume = False

            if event.type == pygame.MOUSEMOTION:
                if self.dragging_volume:
                    self.update_volume_with_mouse(event.pos)

        return True

    # =========================================================
    # TAB SWITCHING
    # =========================================================

    def switch_tab(self, direction):
        self.tab = (self.tab + direction) % 2
        self.selected = 0
        self.waiting_for_key = None

    # =========================================================
    # MOUSE
    # =========================================================
    def handle_mouse_click(self, mouse_pos):
        # --- TAB CLICK ---
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(mouse_pos):
                self.tab = i
                self.selected = 0
                return

        # --- OPTION CLICK ---
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                self.activate_option()
                return
            
    def update_volume_with_mouse(self, mouse_pos):
        x, y = mouse_pos

        slider_x = 860 - 200
        slider_width = 180

        relative_x = max(0, min(slider_width, x - slider_x))
        settings.master_volume = relative_x / slider_width
        settings.apply_audio_settings()

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self, dt):
        pass

    # =========================================================
    # OPTION LOGIC
    # =========================================================

    def option_count(self):
        return len(self.game_options) if self.tab == 0 else len(self.keybind_options)

    def activate_option(self):

        if self.tab == 0:

            if self.selected == 0:
                settings.independent_turret = not settings.independent_turret

            elif self.selected == 1:
                settings.bullet_can_hit_self = not settings.bullet_can_hit_self

            elif self.selected == 2:
                settings.current_resolution_index = (
                    settings.current_resolution_index + 1
                ) % len(settings.windowed_resolutions)
                apply_display_settings(self.state_machine)

            elif self.selected == 3:
                settings.fullscreen = not settings.fullscreen
                apply_display_settings(self.state_machine)

        else:
            key_map = [
                "p1_turret_left",
                "p1_turret_right",
                "p2_turret_left",
                "p2_turret_right",
            ]
            self.waiting_for_key = key_map[self.selected]

    # =========================================================
    # RENDER
    # =========================================================
    def render(self, screen):
        screen.fill((35, 30, 45))  # pastel tím đậm nền

        title_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 48)
        font = pygame.font.SysFont(None, 34)

        # =====================================================
        # TITLE
        # =====================================================
        title = title_font.render("SETTINGS", True, (255, 180, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 60)))

        # =====================================================
        # TABS (Cute Rounded)
        # =====================================================
        self.tab_rects = []

        for i, tab_name in enumerate(self.tabs):

            tab_rect = pygame.Rect(250 + i * 220, 110, 200, 50)
            self.tab_rects.append(tab_rect)

            if i == self.tab:
                color = (200, 160, 255)
            else:
                color = (90, 70, 120)

            pygame.draw.rect(screen, color, tab_rect, border_radius=25)

            text = font.render(tab_name, True, (40, 20, 60))
            screen.blit(text, text.get_rect(center=tab_rect.center))

        # =====================================================
        # OPTIONS PANEL (Glass Style)
        # =====================================================
        panel_rect = pygame.Rect(180, 200, 760, 350)

        glass = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        glass.fill((255, 255, 255, 30))  # transparency
        screen.blit(glass, panel_rect.topleft)

        pygame.draw.rect(screen, (180, 150, 255), panel_rect, 2, border_radius=20)

        options = self.game_options if self.tab == 0 else self.keybind_options

        start_y = 240
        spacing = 60
        label_x = 240
        value_x = 860

        self.option_rects = []

        for i, option in enumerate(options):
            y = start_y + i * spacing

            option_rect = pygame.Rect(200, y - 10, 720, 50)
            self.option_rects.append(option_rect)

            is_selected = (i == self.selected)

            # Glow highlight
            if is_selected:
                highlight = pygame.Rect(200, y - 10, 720, 50)
                pygame.draw.rect(screen, (255, 200, 255), highlight, 2, border_radius=20)

            label_color = (255, 220, 255) if is_selected else (220, 200, 255)
            label_surface = font.render(option, True, label_color)
            screen.blit(label_surface, (label_x, y))

            # ============================
            # SETTINGS TAB
            # ============================
            if self.tab == 0:

                enabled = None  # reset mỗi vòng lặp

                if i == 0:
                    enabled = settings.independent_turret

                elif i == 1:
                    enabled = settings.bullet_can_hit_self

                elif i == 2:  # Resolution
                    res = settings.windowed_resolutions[
                        settings.current_resolution_index
                    ]
                    value_text = f"{res[0]} x {res[1]}"
                    value_surface = font.render(value_text, True, (180, 200, 255))
                    screen.blit(value_surface,
                                value_surface.get_rect(right=value_x, centery=y + 15))
                    continue

                elif i == 3:
                    enabled = settings.fullscreen

                elif i == 4:  # Master Volume
                    volume = settings.master_volume
                    percent = int(volume * 100)

                    slider_rect = pygame.Rect(value_x - 200, y + 5, 180, 8)
                    pygame.draw.rect(screen, (80, 70, 100), slider_rect, border_radius=4)

                    fill_width = int(180 * volume)
                    fill_rect = pygame.Rect(value_x - 200, y + 5, fill_width, 8)
                    pygame.draw.rect(screen, (200, 160, 255), fill_rect, border_radius=4)

                    knob_x = slider_rect.x + fill_width
                    pygame.draw.circle(screen, (255, 255, 255),
                                    (knob_x, slider_rect.centery), 10)

                    value_surface = font.render(f"{percent}%", True, (220, 200, 255))
                    screen.blit(value_surface,
                                value_surface.get_rect(right=value_x, centery=y + 10))

                    continue

                # 👇 CHỈ vẽ pill nếu enabled không phải None
                if enabled is not None:
                    pill_rect = pygame.Rect(value_x - 120, y - 5, 100, 35)

                    if enabled:
                        pygame.draw.rect(screen, (160, 120, 255),
                                        pill_rect, border_radius=20)
                        circle_x = pill_rect.right - 18
                    else:
                        pygame.draw.rect(screen, (80, 70, 100),
                                        pill_rect, border_radius=20)
                        circle_x = pill_rect.left + 18

                    pygame.draw.circle(screen, (255, 255, 255),
                                    (circle_x, pill_rect.centery), 14)

            # ============================
            # KEYBINDS TAB
            # ============================
            else:
                key_map = [
                    "p1_turret_left",
                    "p1_turret_right",
                    "p2_turret_left",
                    "p2_turret_right",
                ]

                key_name = pygame.key.name(
                    settings.keybinds[key_map[i]]
                ).upper()

                capsule_rect = pygame.Rect(value_x - 140, y - 8, 120, 38)

                pygame.draw.rect(screen,
                                (120, 100, 180),
                                capsule_rect,
                                border_radius=18)

                key_surface = font.render(key_name, True, (255, 255, 255))
                screen.blit(key_surface,
                            key_surface.get_rect(center=capsule_rect.center))

        # =====================================================
        # Waiting For Key
        # =====================================================
        if self.waiting_for_key:
            wait_font = pygame.font.SysFont(None, 40)
            wait_text = wait_font.render(
                "Press new key...",
                True,
                (255, 150, 200)
            )
            screen.blit(wait_text,
                        wait_text.get_rect(center=(screen.get_width() // 2, 580)))