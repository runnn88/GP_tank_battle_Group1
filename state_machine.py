class StateMachine:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self._registry = {}
        self.current_state = None

    def register_state(self, name, state_class):
        self._registry[name] = state_class

    def change_state(self, name, **kwargs):
        state_class = self._registry.get(name)

        if not state_class:
            raise ValueError(f"State '{name}' is not registered.")

        self.current_state = state_class(self, **kwargs)

    def handle_events(self):
        return self.current_state.handle_events()

    def update(self, dt):
        self.current_state.update(dt)

    def render(self):
        self.current_state.render(self.screen)