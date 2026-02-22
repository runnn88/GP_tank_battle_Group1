import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from state_machine import StateMachine

from states.start_state import StartState
from states.gameplay_state import GameplayState
from states.game_over_state import GameOverState


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tank Battle: Chaos Maze")
    clock = pygame.time.Clock()

    state_machine = StateMachine(screen)

    # Register states here
    state_machine.register_state("start", StartState)
    state_machine.register_state("gameplay", GameplayState)
    state_machine.register_state("gameover", GameOverState)

    state_machine.change_state("start")

    while True:
        dt = clock.tick(FPS) / 1000.0

        if not state_machine.handle_events():
            break

        state_machine.update(dt)
        state_machine.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()