import pygame
from states.base_state import BaseState

class PauseState(BaseState):
    def __init__(self, state_machine, previous_state):
        super().__init__(state_machine)

        self.previous_state = previous_state

        self.options = [
            "Resume",
            "Settings",
            "Restart Match",
            "Main Menu",
        ]

        self.selected_index = 0
        self.option_rects = []

        self.title_font = pygame.font.SysFont(None, 72)
        self.option_font = pygame.font.SysFont(None, 42)
        
    # ======================================================
    # INPUT
    # ======================================================
    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            # KEYBOARD
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self._resume_game()

                elif event.key == pygame.K_UP:
                    self.selected_index = (
                        self.selected_index - 1
                    ) % len(self.options)

                elif event.key == pygame.K_DOWN:
                    self.selected_index = (
                        self.selected_index + 1
                    ) % len(self.options)

                elif event.key == pygame.K_RETURN:
                    self._activate_selected_option()
                
            # MOUSE CLICK
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()

                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_index = i
                            self._activate_selected_option()

        return True
    
    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, dt):
        pass

    # ======================================================
    # RENDER
    # ======================================================
    # def render(self, screen):

    #     # Render gameplay behind
    #     self.previous_state.render(screen)

    #     # Dark overlay
    #     overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    #     overlay.fill((0, 0, 0, 160))
    #     screen.blit(overlay, (0, 0))

    #     # Title
    #     title_text = self.title_font.render("PAUSED", True, (255, 255, 255))
    #     title_rect = title_text.get_rect(
    #         center=(screen.get_width() // 2, 150)
    #     )
    #     screen.blit(title_text, title_rect)

    #     # Reset option rects
    #     self.option_rects = []

    #     mouse_pos = pygame.mouse.get_pos()

    #     # Draw menu options
    #     for i, option in enumerate(self.options):
    #         option_text = self.option_font.render(option, True, (255, 255, 255))
    #         option_rect = option_text.get_rect(
    #             center=(screen.get_width() // 2, 250 + i * 60)
    #         )

    #         # If mouse is over this option → update selection
    #         if option_rect.collidepoint(mouse_pos):
    #             self.selected_index = i

    #         # Highlight based on selected_index
    #         if i == self.selected_index:
    #             color = (0, 255, 200)  # highlight color
    #         else:
    #             color = (255, 255, 255)

    #         # Render with correct color
    #         option_text = self.option_font.render(option, True, color)
    #         option_rect = option_text.get_rect(
    #             center=(screen.get_width() // 2, 250 + i * 60)
    #         )

    #         screen.blit(option_text, option_rect)
    #         self.option_rects.append(option_rect)
    
    # ======================================================
    # ACTIONS
    # ======================================================
    def _resume_game(self):
        self.state_machine.current_state = self.previous_state

    def _activate_selected_option(self):

        selected_option = self.options[self.selected_index]

        if selected_option == "Resume":
            self._resume_game()

        elif selected_option == "Settings":
            self.state_machine.change_state(
                "settings",
                previous_state=self
            )

        elif selected_option == "Restart Match":
            self.state_machine.change_state("gameplay")

        elif selected_option == "Main Menu":
            self.state_machine.change_state("start")
    
    def render(self, screen):
        # Render gameplay phía sau
        self.previous_state.render(screen)

        # =====================================================
        # Dark + blur feel overlay
        # =====================================================
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 10, 35, 180))  # tím đậm trong suốt
        screen.blit(overlay, (0, 0))

        width = screen.get_width()
        height = screen.get_height()

        # =====================================================
        # Glass Panel
        # =====================================================
        panel_rect = pygame.Rect(
            width // 2 - 350,
            height // 2 - 250,
            700,
            500
        )

        glass = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        glass.fill((255, 255, 255, 35))
        screen.blit(glass, panel_rect.topleft)

        pygame.draw.rect(screen, (200, 160, 255),
                        panel_rect, 2, border_radius=30)

        # =====================================================
        # TITLE
        # =====================================================
        title_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 70)
        title_text = title_font.render("PAUSED", True, (255, 180, 255))
        screen.blit(title_text,
                    title_text.get_rect(center=(width // 2,
                                                panel_rect.top + 90)))

        # =====================================================
        # OPTIONS
        # =====================================================
        self.option_rects = []
        mouse_pos = pygame.mouse.get_pos()

        start_y = panel_rect.top + 180
        spacing = 75

        for i, option in enumerate(self.options):

            y = start_y + i * spacing

            option_rect = pygame.Rect(
                width // 2 - 220,
                y - 25,
                440,
                55
            )

            is_selected = (i == self.selected_index)

            # Hover bằng chuột
            if option_rect.collidepoint(mouse_pos):
                self.selected_index = i
                is_selected = True

            # -------------------------------------------------
            # Button background
            # -------------------------------------------------
            if is_selected:
                pygame.draw.rect(screen,
                                (210, 170, 255),
                                option_rect,
                                border_radius=30)
            else:
                pygame.draw.rect(screen,
                                (90, 70, 120),
                                option_rect,
                                border_radius=30)

            # -------------------------------------------------
            # Text
            # -------------------------------------------------
            text_color = (40, 20, 60) if is_selected else (230, 220, 255)

            option_font = pygame.font.SysFont(None, 42)
            text_surface = option_font.render(option, True, text_color)
            screen.blit(text_surface,
                        text_surface.get_rect(center=option_rect.center))

            self.option_rects.append(option_rect)