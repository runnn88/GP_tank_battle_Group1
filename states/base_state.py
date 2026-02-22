class BaseState:
    def __init__(self, state_machine):
        self.state_machine = state_machine

    def handle_events(self):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def render(self, screen):
        raise NotImplementedError