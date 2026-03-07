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

    resized = set()

    def notify_resize(state):
        if state is None:
            return
        state_id = id(state)
        if state_id in resized:
            return
        resized.add(state_id)

        if hasattr(state, "on_resize"):
            state.on_resize(new_screen)

        prev = getattr(state, "previous_state", None)
        if prev is not None:
            notify_resize(prev)

    notify_resize(state_machine.current_state)
