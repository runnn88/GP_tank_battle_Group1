import pygame
from states.base_state import BaseState
from game.settings_manager import settings
from utils.display_manager import apply_display_settings


class SettingsState(BaseState):
    def __init__(self, state_machine, previous_state=None):
        super().__init__(state_machine)
        self.previous_state = previous_state

        self.tab = 0  # 0 = Settings, 1 = Keybinds
        self.selected = 0
        self.waiting_for_key = None

        self.tabs = ["SETTINGS", "KEYBINDS"]

        self.game_options = [
            "Independent Turret",
            "Bullet Can Hit Self",
            "Resolution",
            "Fullscreen"
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
                self.handle_mouse_click(pygame.mouse.get_pos())

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
        x, y = mouse_pos

        # --- Check Tab Click ---
        for i in range(len(self.tabs)):
            tab_rect = pygame.Rect(100 + i * 200, 40, 180, 40)
            if tab_rect.collidepoint(mouse_pos):
                self.tab = i
                self.selected = 0
                return

        # --- Check Option Click ---
        start_y = 140
        spacing = 45

        options = self.game_options if self.tab == 0 else self.keybind_options

        for i in range(len(options)):
            option_rect = pygame.Rect(100, start_y + i * spacing, 600, 40)
            if option_rect.collidepoint(mouse_pos):
                self.selected = i
                self.activate_option()
                break

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
        screen.fill((25, 25, 25))
        font = pygame.font.SysFont(None, 36)

        # -------------------------
        # Draw Tabs
        # -------------------------
        for i, tab_name in enumerate(self.tabs):

            tab_rect = pygame.Rect(100 + i * 200, 40, 180, 40)

            color = (80, 80, 80)
            if i == self.tab:
                color = (150, 150, 150)

            pygame.draw.rect(screen, color, tab_rect)
            text = font.render(tab_name, True, (0, 0, 0))
            screen.blit(text, (tab_rect.x + 20, tab_rect.y + 5))

        # -------------------------
        # Draw Options
        # -------------------------
        options = self.game_options if self.tab == 0 else self.keybind_options
        
        start_y = 140
        spacing = 50
        label_x = 140
        value_x = 650  # right-aligned value column

        for i, option in enumerate(options):

            y = start_y + i * spacing

            # --------------------------------------------------
            # Selection Highlight
            # --------------------------------------------------
            is_selected = (i == self.selected)

            label_color = (255, 255, 0) if is_selected else (220, 220, 220)

            # --------------------------------------------------
            # SETTINGS TAB
            # --------------------------------------------------
            if self.tab == 0:

                # Determine value text + color
                if option == "Independent Turret":
                    enabled = settings.independent_turret
                    value_text = "ON" if enabled else "OFF"
                    value_color = (0, 255, 120) if enabled else (255, 80, 80)

                elif option == "Bullet Can Hit Self":
                    enabled = settings.bullet_can_hit_self
                    value_text = "ON" if enabled else "OFF"
                    value_color = (0, 255, 120) if enabled else (255, 80, 80)

                elif option == "Resolution":
                    res = settings.windowed_resolutions[
                        settings.current_resolution_index
                    ]
                    value_text = f"{res[0]} x {res[1]}"
                    value_color = (180, 180, 255)

                elif option == "Fullscreen":
                    enabled = settings.fullscreen
                    value_text = "ON" if enabled else "OFF"
                    value_color = (0, 255, 120) if enabled else (255, 80, 80)

                # Render label
                label_surface = font.render(option, True, label_color)
                screen.blit(label_surface, (label_x, y))

                # Render value (right aligned)
                value_surface = font.render(value_text, True, value_color)
                value_rect = value_surface.get_rect(right=value_x, centery=y + 12)
                screen.blit(value_surface, value_rect)

            # --------------------------------------------------
            # KEYBINDS TAB
            # --------------------------------------------------
            else:
                key_map = [
                    "p1_turret_left",
                    "p1_turret_right",
                    "p2_turret_left",
                    "p2_turret_right",
                ]

                key_name = pygame.key.name(settings.keybinds[key_map[i]]).upper()

                label_surface = font.render(option, True, label_color)
                screen.blit(label_surface, (label_x, y))

                key_surface = font.render(f"[ {key_name} ]", True, (100, 200, 255))
                key_rect = key_surface.get_rect(right=value_x, centery=y + 12)
                screen.blit(key_surface, key_rect)
        # -------------------------
        # Waiting For Key
        # -------------------------
        if self.waiting_for_key:
            wait_text = font.render("Press new key...", True, (255, 80, 80))
            screen.blit(wait_text, (120, 420))