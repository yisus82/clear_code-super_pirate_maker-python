import pygame


class Transition:
    def __init__(self, toggle):
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False
        self.border_width = 0
        self.direction = 1

    def update(self, dt):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        center = (window_width / 2, window_height / 2)
        radius = pygame.Vector2(center).magnitude()
        threshold = radius + 100
        self.border_width += 1000 * dt * self.direction
        if self.border_width >= threshold:
            self.direction = -1
            self.toggle()
        if self.border_width < 0:
            self.active = False
            self.border_width = 0
            self.direction = 1
        pygame.draw.circle(
            self.display_surface,
            "black",
            center,
            radius,
            int(self.border_width),
        )
