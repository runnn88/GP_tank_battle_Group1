import pygame
from states.base_state import BaseState


class GameOverState(BaseState):
    def __init__(self, state_machine, winner):
        super().__init__(state_machine)
        self.winner = winner
        self.font = pygame.font.SysFont(None, 64)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                self.state_machine.change_state("start")

        return True

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        text = self.font.render(self.winner, True, (255, 0, 0))
        rect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, rect)