import pygame
from settings import COLLISION_OFFSET
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
        damage=1,
    ):
        super().__init__(position, animations, groups, status, pivot, has_mask=True)
        self.enemy_type = enemy_type
        self.damage = damage

    def damage_player(self, player):
        player.take_damage(self.damage)


class Spikes(Enemy):
    def __init__(
        self,
        position,
        groups,
        animations,
    ):
        super().__init__("spikes", position, groups, animations, damage=5)


class Tooth(Enemy):
    def __init__(
        self,
        position,
        groups,
        animations,
        orientation="left",
        collision_sprites=[],
    ):
        super().__init__("tooth", position, groups, animations, damage=20)
        self.left_frames = animations.copy()
        self.right_frames = self.flip_frames(animations)
        self.orientation = orientation
        self.set_orientation(orientation)
        self.direction = (
            pygame.Vector2(1, 0) if orientation == "right" else pygame.Vector2(-1, 0)
        )
        self.collision_sprites = collision_sprites
        self.speed = 120
        self.idle_timer = Timer(2000)
        self.idle_timer.activate()

    def update_status(self):
        self.status = "idle" if self.idle_timer.active else "run"

    def flip_frames(self, frames):
        return {
            key: [pygame.transform.flip(value, True, False) for value in values]
            for key, values in frames.copy().items()
        }

    def update_orientation(self):
        if self.direction.x == 1:
            self.set_orientation("right")
        elif self.direction.x == -1:
            self.set_orientation("left")

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.orientation == "right":
            self.frames = self.right_frames
        else:
            self.frames = self.left_frames

    def sprite_left_collide(self):
        left_rect = pygame.Rect(
            self.hitbox.topleft, (COLLISION_OFFSET, self.hitbox.height)
        )
        for sprite in self.collision_sprites:
            sprite_rect = pygame.Rect(
                sprite.hitbox.topright, (COLLISION_OFFSET, sprite.hitbox.height)
            )
            if sprite_rect.colliderect(left_rect):
                return sprite
        return None

    def sprite_right_collide(self):
        right_rect = pygame.Rect(
            self.hitbox.topright, (COLLISION_OFFSET, self.hitbox.height)
        )
        for sprite in self.collision_sprites:
            sprite_rect = pygame.Rect(
                sprite.hitbox.topleft, (COLLISION_OFFSET, sprite.hitbox.height)
            )
            if sprite_rect.colliderect(right_rect):
                return sprite
        return None

    def sprite_down_collide(self):
        point = (
            self.hitbox.bottomleft
            if self.direction.x == -1
            else self.hitbox.bottomright
        )
        for sprite in self.collision_sprites:
            if sprite.hitbox.collidepoint(point):
                return sprite
        return None

    def horizontal_collide(self):
        if self.direction.x > 0:
            if self.sprite_right_collide():
                self.idle_timer.activate()
        elif self.direction.x < 0:
            if self.sprite_left_collide():
                self.idle_timer.activate()

    def check_on_floor(self):
        return self.sprite_down_collide() is not None

    def move(self, dt):
        self.hitbox.move_ip(self.direction.x * self.speed * dt, 0)
        self.horizontal_collide()
        if self.sprite_down_collide() is None:
            self.hitbox.move_ip(-self.direction.x * self.speed * dt, 0)
            self.idle_timer.activate()

    def resume_move(self):
        self.direction.x *= -1
        self.set_orientation("right" if self.direction.x == 1 else "left")

    def update(self, dt):
        if not self.check_on_floor():
            self.kill()
        self.update_orientation()
        if self.idle_timer.active:
            self.idle_timer.update()
            if not self.idle_timer.active:
                self.resume_move()
        else:
            self.move(dt)
        self.update_status()
        super().update(dt)
        self.rect = self.image.get_rect(bottomleft=self.hitbox.bottomleft)


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
        super().__init__("shell", position, groups, animations, damage=0)
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
            "pearl", position, groups, {"idle": [surface]}, pivot="topleft", damage=10
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
