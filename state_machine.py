class StateMachine:
    def __init__(self, screen):
        self.screen = screen
        self._registry = {}
        self.current_state = None

    def set_screen(self, new_screen):
        self.screen = new_screen

    def register_state(self, name, state_class):
        self._registry[name] = state_class

    def change_state(self, name, **kwargs):
        state_class = self._registry.get(name)
        self.current_state = state_class(self, **kwargs)

    def handle_events(self):
        return self.current_state.handle_events()

    def update(self, dt):
        self.current_state.update(dt)

    def render(self):
        self.current_state.render(self.screen)