import pygame
from states.base_state import BaseState


class StartState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        # Fonts for game title and button text
        self.title_font = pygame.font.SysFont(None, 96)
        self.button_font = pygame.font.SysFont(None, 48)

        # Define buttons in the middle of the screen
        screen_rect = self.state_machine.screen.get_rect()

        # "Press Start" button
        self.button_rect = pygame.Rect(0, 0, 320, 90)
        self.button_rect.center = (screen_rect.centerx, screen_rect.centery + 80)

        # "Quit" button (placed below Start)
        self.quit_button_rect = pygame.Rect(0, 0, 240, 80)
        self.quit_button_rect.center = (screen_rect.centerx, screen_rect.centery + 200)

        # Pre-render button labels
        self.button_text = self.button_font.render("Press Start", True, (0, 0, 0))
        self.quit_text = self.button_font.render("Quit", True, (0, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle mouse clicks on buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(event.pos):
                    self.state_machine.change_state("gameplay")
                elif self.quit_button_rect.collidepoint(event.pos):
                    return False

        return True

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((20, 20, 20))

        # Draw game title
        title_text = self.title_font.render("Tank Battle: Chaos Maze", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 150))
        screen.blit(title_text, title_rect)

        # Draw "Press Start" button
        pygame.draw.rect(screen, (240, 240, 240), self.button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 4)
        button_text_rect = self.button_text.get_rect(center=self.button_rect.center)
        screen.blit(self.button_text, button_text_rect)

        # Draw "Quit" button
        pygame.draw.rect(screen, (220, 80, 80), self.quit_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.quit_button_rect, 4)
        quit_text_rect = self.quit_text.get_rect(center=self.quit_button_rect.center)
        screen.blit(self.quit_text, quit_text_rect)