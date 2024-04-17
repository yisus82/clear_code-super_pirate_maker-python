import pygame


class Transition:
    def __init__(self, toggle):
        self.display_surface = pygame.display.get_surface()
        self.window_width = self.display_surface.get_width()
        self.window_height = self.display_surface.get_height()
        self.toggle = toggle
        self.active = False
        self.border_width = 0
        self.direction = 1
        self.center = (self.window_width / 2, self.window_height / 2)
        self.radius = pygame.Vector2(self.center).magnitude()
        self.threshold = self.radius + 100

    def update(self, dt):
        self.border_width += 1000 * dt * self.direction
        if self.border_width >= self.threshold:
            self.direction = -1
            self.toggle()
        if self.border_width < 0:
            self.active = False
            self.border_width = 0
            self.direction = 1
        pygame.draw.circle(
            self.display_surface,
            "black",
            self.center,
            self.radius,
            int(self.border_width),
        )
