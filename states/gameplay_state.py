from states.base_state import BaseState
from game.level import Level
from game.tank import Tank
from ui.hud import HUD
from config import PLAYER1_CONTROLS, PLAYER2_CONTROLS


class GameplayState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        self.level = Level("data/maps/level1.txt")
        self.hud = HUD()

        self.player1 = Tank(self.level.spawn_p1,
                            PLAYER1_CONTROLS, (0, 200, 0))
        self.player2 = Tank(self.level.spawn_p2,
                            PLAYER2_CONTROLS, (200, 0, 0))

    def handle_events(self):
        import pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.player1.handle_event(event)
            self.player2.handle_event(event)

        return True

    def update(self, dt):
        self.player1.update(dt, self.level.walls, self.player2)
        self.player2.update(dt, self.level.walls, self.player1)

        if not self.player1.alive:
            self.state_machine.change_state(
                "gameover", winner="Player 2 Wins!"
            )

        if not self.player2.alive:
            self.state_machine.change_state(
                "gameover", winner="Player 1 Wins!"
            )

    def render(self, screen):
        screen.fill((30, 30, 30))
        self.level.render(screen)

        self.player1.render(screen)
        self.player2.render(screen)

        self.hud.render(screen, self.player1, self.player2)