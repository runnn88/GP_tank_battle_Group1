from states.base_state import BaseState
from game.level import Level
from game.tank import Tank
from ui.hud import HUD
from config import (
    PLAYER1_CONTROLS,
    PLAYER2_CONTROLS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    UI_SIDE_WIDTH,
)
import pygame


class GameplayState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        self.level = Level("data/maps/level1.txt")
        self.hud = HUD()

        self.player1 = Tank(self.level.spawn_p1,
                            PLAYER1_CONTROLS, (0, 200, 0))
        self.player2 = Tank(self.level.spawn_p2,
                            PLAYER2_CONTROLS, (200, 0, 0))

        # Compute offset so the level is centered between left/right UI banners
        play_area_width = SCREEN_WIDTH - 2 * UI_SIDE_WIDTH
        offset_x = UI_SIDE_WIDTH + (play_area_width - self.level.width) / 2
        offset_y = (SCREEN_HEIGHT - self.level.height) / 2
        self.level_offset = pygame.Vector2(offset_x, offset_y)

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
        self.level.render(screen, self.level_offset)

        self.player1.render(screen, self.level_offset)
        self.player2.render(screen, self.level_offset)

        self.hud.render(screen, self.player1, self.player2)