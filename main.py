import pygame
from state_machine import StateMachine

from states.start_state import StartState
from states.gameplay_state import GameplayState
from states.game_over_state import GameOverState
from states.pause_state import PauseState         
from states.settings_state import SettingsState   

from game.settings_manager import settings


def main():
    pygame.init()

    if settings.fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(settings.resolution)

    pygame.display.set_caption("Tank Battle: Chaos Maze")
    clock = pygame.time.Clock()

    state_machine = StateMachine(screen)

    # ✅ Register ALL states clearly
    state_machine.register_state("start", StartState)
    state_machine.register_state("gameplay", GameplayState)
    state_machine.register_state("gameover", GameOverState)
    state_machine.register_state("pause", PauseState)
    state_machine.register_state("settings", SettingsState)

    state_machine.change_state("start")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  

        running = state_machine.handle_events()
        state_machine.update(dt)
        state_machine.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()