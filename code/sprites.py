import pygame
from settings import ANIMATION_SPEED, TILE_SIZE


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.position = position


class Animated(Generic):
    def __init__(
        self,
        position,
        frames={"idle": [pygame.Surface((TILE_SIZE, TILE_SIZE))]},
        groups=[],
        status="idle",
        centered=False,
    ):
        super().__init__(position, frames[status][0], groups)
        self.status = status
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.status][self.frame_index]
        self.animation_speed = ANIMATION_SPEED
        self.centered = centered
        if self.centered:
            self.rect = self.image.get_rect(center=position)
        else:
            self.rect = self.image.get_rect(topleft=position)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames[self.status]):
            self.frame_index = 0
        self.image = self.frames[self.status][int(self.frame_index)]
        if self.centered:
            self.rect = self.image.get_rect(center=self.position)
        else:
            self.rect = self.image.get_rect(topleft=self.position)

    def update(self, dt):
        self.animate(dt)