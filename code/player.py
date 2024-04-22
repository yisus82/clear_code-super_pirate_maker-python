import pygame
from sprites import Animated


class Player(Animated):
    def __init__(self, position, groups, animations=[], status="idle_right"):
        super().__init__(position, animations, groups, status)
        self.direction = pygame.Vector2()
        self.speed = 300

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update_status(self):
        direction = self.status.split("_")[1]
        if self.direction.x == 1:
            direction = "right"
        elif self.direction.x == -1:
            direction = "left"
        self.status = f"idle_{direction}"

    def move(self, dt):
        self.position += self.direction * self.speed * dt
        self.rect.topleft = (round(self.position.x), round(self.position.y))

    def update(self, dt):
        self.input()
        self.update_status()
        self.move(dt)
        super().update(dt)
