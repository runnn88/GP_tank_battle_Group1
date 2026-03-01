import pygame
from game.settings_manager import settings


def apply_display_settings(state_machine):
    if settings.fullscreen:
        new_screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN
        )
    else:
        new_screen = pygame.display.set_mode(
            settings.resolution
        )

    state_machine.set_screen(new_screen)