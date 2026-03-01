import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from state_machine import StateMachine

from states.start_state import StartState
from states.gameplay_state import GameplayState
from states.game_over_state import GameOverState
from states.settings_state import SettingsState
from states.pause_state import PauseState

from game.settings_manager import settings


def main():
    pygame.init()

    if settings.fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        # screen = pygame.display.set_mode(settings.resolution)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    pygame.display.set_caption("Tank Battle: Chaos Maze")
    clock = pygame.time.Clock()

    state_machine = StateMachine(screen)

    # Register states here
    state_machine.register_state("start", StartState)
    state_machine.register_state("gameplay", GameplayState)
    state_machine.register_state("gameover", GameOverState)
    state_machine.register_state("settings", SettingsState)
    state_machine.register_state("pause", PauseState)

    state_machine.change_state("start")
    
    while True:
        dt = clock.tick(settings.fps_cap) / 1000.0

        if not state_machine.handle_events():
            break

        state_machine.update(dt)
        state_machine.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()