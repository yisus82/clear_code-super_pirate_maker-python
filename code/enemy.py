import pygame
from sprites import Animated


class Enemy(Animated):
    def __init__(
        self,
        enemy_type,
        position,
        groups,
        animations,
        status="idle",
        pivot="bottomleft",
    ):
        super().__init__(position, animations, groups, status, pivot)
        self.enemy_type = enemy_type


class Spikes(Enemy):
    def __init__(
        self,
        position,
        groups,
        animations,
    ):
        super().__init__("spikes", position, groups, animations)


class Tooth(Enemy):
    def __init__(
        self,
        position,
        groups,
        animations,
        orientation="left",
    ):
        super().__init__("tooth", position, groups, animations)
        self.frames = animations.copy()
        self.orientation = orientation
        self.set_orientation(orientation)

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.orientation == "right":
            for key, values in self.frames.items():
                self.frames[key] = [
                    pygame.transform.flip(value, True, False) for value in values
                ]


class Shell(Enemy):
    def __init__(
        self,
        position,
        groups,
        animations,
        orientation="left",
    ):
        super().__init__("shell", position, groups, animations)
        self.frames = animations.copy()
        self.orientation = orientation
        self.set_orientation(orientation)

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.orientation == "right":
            for key, values in self.frames.items():
                self.frames[key] = [
                    pygame.transform.flip(value, True, False) for value in values
                ]
