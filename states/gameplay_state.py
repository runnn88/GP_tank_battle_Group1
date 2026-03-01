import pygame

from states.base_state import BaseState
from states.pause_state import PauseState

from game.level import Level
from game.tank import Tank
from ui.hud import HUD
from config import (
    PLAYER1_CONTROLS,
    PLAYER2_CONTROLS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    UI_SIDE_WIDTH
)

class GameplayState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        self.level = Level("data/maps/level1.txt")
        self.hud = HUD()

        self.player1 = Tank(
            position=self.level.spawn_p1,
            controls=PLAYER1_CONTROLS, 
            color=(0, 200, 0),
            turret_left_key_name="p1_turret_left",
            turret_right_key_name="p1_turret_right"
        )
        
        self.player2 = Tank(
            position=self.level.spawn_p2,
            controls=PLAYER2_CONTROLS, 
            color=(200, 0, 0),
            turret_left_key_name="p2_turret_left",
            turret_right_key_name="p2_turret_right"
        )

        # Offset to place the level between left and right HUD panels.
        # If the level is narrower than the play area, center it.
        # If it's wider, pin the left edge to the inside of the left HUD panel
        # so it is not hidden underneath the banner.
        play_area_width = SCREEN_WIDTH - 2 * UI_SIDE_WIDTH
        if self.level.width <= play_area_width:
            offset_x = UI_SIDE_WIDTH + (play_area_width - self.level.width) / 2
        else:
            offset_x = UI_SIDE_WIDTH

        # Vertically center if it fits, otherwise pin to top.
        if self.level.height <= SCREEN_HEIGHT:
            offset_y = (SCREEN_HEIGHT - self.level.height) / 2
        else:
            offset_y = 0
        self.level_offset = pygame.Vector2(offset_x, offset_y)

        # Explosion timer
        self.explosion_timer = 0.0
        self.explosion_duration = 5.0  # Duration of explosion effect
        self.waiting_for_explosion = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.player1.handle_event(event)
            self.player2.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not isinstance(self.state_machine.current_state, PauseState):
                        # self.state_machine.change_state(
                        #     PauseState(self.state_machine, self)
                        # )
                        self.state_machine.current_state = PauseState(self.state_machine, self)

        return True

    def update(self, dt):
        # self.player1.update(dt, self.level.walls, self.player2)
        # self.player2.update(dt, self.level.walls, self.player1)

        # if not self.player1.alive:
        #     self.state_machine.change_state(
        #         "gameover", winner="Player 2 Wins!"
        #     )

        # if not self.player2.alive:
        #     self.state_machine.change_state(
        #         "gameover", winner="Player 1 Wins!"
        #     )

        if self.waiting_for_explosion:
            # Update explosion timer
            self.explosion_timer += dt
            if self.explosion_timer >= self.explosion_duration:
                # Transition to gameover state after explosion effect
                if not self.player1.alive:
                    self.state_machine.change_state(
                        "gameover", winner="Player 2 Wins!"
                    )
                elif not self.player2.alive:
                    self.state_machine.change_state(
                        "gameover", winner="Player 1 Wins!"
                    )
            return  # Skip updating players and level during explosion

        # Update players and check for gameover condition
        self.player1.update(dt, self.level.walls, self.player2)
        self.player2.update(dt, self.level.walls, self.player1)

        if not self.player1.alive or not self.player2.alive:
            self.waiting_for_explosion = True
            self.explosion_timer = 0.0  # Start explosion timer

    def render(self, screen):
        screen.fill((30, 30, 30))

        # Draw level and tanks centered in the middle play area
        self.level.render(screen, self.level_offset)
        
        self.player1.render(screen, self.level_offset)
        self.player2.render(screen, self.level_offset)

        # Draw side HUD panels on top
        self.hud.render(screen, self.player1, self.player2)