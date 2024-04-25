import pygame
from sprites import Animated
from timer import Timer


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
        projectile_image,
        projectile_groups,
        player,
        orientation="left",
    ):
        super().__init__("shell", position, groups, animations)
        self.left_frames = animations.copy()
        self.right_frames = self.flip_frames(animations)
        self.orientation = orientation
        self.set_orientation(orientation)
        self.projectile_image = projectile_image
        self.projectile_groups = projectile_groups
        self.player = player
        self.attack_cooldown = Timer(2000)

    def flip_frames(self, frames):
        return {
            key: [pygame.transform.flip(value, True, False) for value in values]
            for key, values in frames.copy().items()
        }

    def set_orientation(self, orientation):
        self.orientation = orientation
        self.frames = self.left_frames if orientation == "left" else self.right_frames

    def is_player_in_attack_distance(self):
        horizontal_distance = abs(self.player.rect.centerx - self.rect.centerx)
        vertical_distance = abs(self.player.rect.centery - self.rect.centery)
        return horizontal_distance < 500 and vertical_distance < 100

    def can_attack(self):
        return self.is_player_in_attack_distance() and not self.attack_cooldown.active

    def update_status(self):
        if self.can_attack():
            self.status = "attack"
            self.attack_cooldown.activate()

    def update_attack_cooldown(self):
        self.attack_cooldown.update()

    def attack(self):
        if self.status == "attack":
            if self.player.rect.centerx < self.rect.centerx:
                self.set_orientation("left")
            else:
                self.set_orientation("right")
            if int(self.frame_index) == 2:
                pearl_direction = (
                    pygame.Vector2(-1, 0)
                    if self.orientation == "left"
                    else pygame.Vector2(1, 0)
                )
                offset = (
                    (pearl_direction * 50) + pygame.Vector2(0, -10)
                    if self.orientation == "left"
                    else (pearl_direction * 20) + pygame.Vector2(0, -10)
                )
                Pearl(
                    self.rect.center + offset,
                    self.projectile_image,
                    self.projectile_groups,
                    pearl_direction,
                )
                self.status = "idle"

    def update(self, dt):
        self.update_attack_cooldown()
        self.update_status()
        self.attack()
        super().update(dt)


class Pearl(Enemy):
    def __init__(self, position, surface, groups, direction):
        super().__init__(
            "pearl", position, groups, {"idle": [surface]}, pivot="topleft"
        )
        self.direction = direction
        self.speed = 150
        self.timer = Timer(4000, self.kill)
        self.timer.activate()

    def move(self, dt):
        self.hitbox.move_ip(self.direction * self.speed * dt)

    def update(self, dt):
        self.move(dt)
        self.timer.update()
        super().update(dt)
