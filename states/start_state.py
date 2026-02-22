import pygame
from states.base_state import BaseState


class StartState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.font = pygame.font.SysFont(None, 64)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                self.state_machine.change_state("gameplay")

        return True

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((20, 20, 20))
        text = self.font.render("Press Any Key to Start", True, (255, 255, 255))
        rect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, rect)