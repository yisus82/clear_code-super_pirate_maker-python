import pygame
from settings import ANIMATION_SPEED, TILE_SIZE
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups, sorting_layer="main"):
        super().__init__(groups)
        self.position = position
        self.image = surface
        self.rect = self.image.get_rect(topleft=self.position)
        self.hitbox = self.rect
        self.sorting_layer = sorting_layer

    def draw_hitbox(self, surface):
        pygame.draw.rect(surface, "red", self.hitbox, 2)


class Mask(Generic):
    def __init__(self, position, size=(TILE_SIZE, TILE_SIZE), groups=[]):
        super().__init__(position, pygame.Surface(size), groups)


class Animated(Generic):
    def __init__(
        self,
        position,
        frames={"idle": [pygame.Surface((TILE_SIZE, TILE_SIZE))]},
        groups=[],
        status="idle",
        pivot="center",
        sorting_layer="main",
    ):
        super().__init__(position, frames[status][0], groups, sorting_layer)
        self.status = status
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.status][self.frame_index]
        self.animation_speed = ANIMATION_SPEED
        self.pivot = pivot
        self.position = (
            (self.position[0], self.position[1] + TILE_SIZE)
            if self.pivot == "bottomleft"
            else self.position
        )
        if self.pivot == "center":
            self.rect = self.image.get_rect(center=self.position)
        elif self.pivot == "bottomleft":
            self.rect = self.image.get_rect(bottomleft=self.position)
        else:
            self.rect = self.image.get_rect(topleft=self.position)
        self.hitbox = self.rect

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames[self.status]):
            self.frame_index = 0
        self.image = self.frames[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self, dt):
        self.animate(dt)


class Coin(Animated):
    def __init__(self, coin_type, position, frames, groups):
        super().__init__(position, frames, groups)
        self.coin_type = coin_type


class Particle(Animated):
    def __init__(
        self,
        position,
        frames={"idle": [pygame.Surface((TILE_SIZE, TILE_SIZE))]},
        groups=[],
        ttl=None,
    ):
        super().__init__(position, frames, groups)
        if ttl:
            self.timer = Timer(ttl, self.kill)
            self.timer.activate()

    def update_timer(self):
        if self.timer:
            self.timer.update()

    def update(self, dt):
        self.update_timer()
        super().update(dt)


class Water(Animated):
    def __init__(self, water_type, position, frames, groups):
        super().__init__(
            position, frames, groups, pivot="topleft", sorting_layer="water"
        )
        self.water_type = water_type


class AnimatedObject(Animated):
    def __init__(
        self,
        object_type,
        object_subtype,
        position,
        frames,
        groups,
        status="idle",
        background=False,
        pivot="topleft",
        sorting_layer="main",
    ):
        super().__init__(position, frames, groups, status, pivot, sorting_layer)
        self.object_type = object_type
        self.object_subtype = object_subtype
        self.background = background
