from math import sin

import pygame
from settings import (
    COLLISION_OFFSET,
    DAMAGE_FORCE,
    GRAVITY,
    JUMP_FORCE,
    PLAYER_HEALTH,
    PLAYER_HITBOX_OFFSET,
    PLAYER_INVULNERABILITY_DURATION,
    PLAYER_SPEED,
)
from sprites import Animated
from timer import Timer


class Player(Animated):
    def __init__(
        self, position, animations, groups, collision_sprites, status="idle_right"
    ):
        super().__init__(
            position, animations, groups, status, "bottomleft", "player", True
        )
        self.collision_sprites = collision_sprites
        self.speed = PLAYER_SPEED
        self.on_floor = False
        self.direction = pygame.Vector2()
        self.orientation = self.status.split("_")[1]
        self.hitbox = self.rect.inflate(*PLAYER_HITBOX_OFFSET)
        self.health = PLAYER_HEALTH
        self.invulnerability_timer = Timer(PLAYER_INVULNERABILITY_DURATION)

    def input(self):
        keys = pygame.key.get_pressed()

        # movement
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        # jump
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = JUMP_FORCE
            self.on_floor = False

    def update_orientation(self):
        if self.direction.x == 1:
            self.orientation = "right"
        elif self.direction.x == -1:
            self.orientation = "left"

    def update_status(self):
        if self.on_floor:
            self.status = (
                f"idle_{self.orientation}"
                if self.direction.x == 0
                else f"run_{self.orientation}"
            )
        else:
            self.status = (
                f"jump_{self.orientation}"
                if self.direction.y < 0
                else f"fall_{self.orientation}"
            )

    def move(self, dt):
        # horizontal movement
        self.hitbox.move_ip(self.direction.x * self.speed * dt, 0)
        self.horizontal_collide()

        # vertical movement
        self.hitbox.move_ip(0, self.direction.y * self.speed * dt)
        self.vertical_collide()

    def apply_gravity(self, dt):
        self.direction.y += GRAVITY * dt

    def check_on_floor(self):
        self.on_floor = self.sprite_down_collide() is not None

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

    def sprite_up_collide(self):
        up_rect = pygame.Rect(
            self.hitbox.topleft, (self.hitbox.width, COLLISION_OFFSET * 2)
        )
        for sprite in self.collision_sprites:
            sprite_rect = pygame.Rect(
                sprite.hitbox.bottomleft, (sprite.hitbox.width, COLLISION_OFFSET)
            )
            if sprite_rect.colliderect(up_rect):
                return sprite
        return None

    def sprite_down_collide(self):
        down_rect = pygame.Rect(
            self.hitbox.bottomleft, (self.hitbox.width, COLLISION_OFFSET)
        )
        for sprite in self.collision_sprites:
            sprite_rect = pygame.Rect(
                sprite.hitbox.topleft, (sprite.hitbox.width, COLLISION_OFFSET)
            )
            if sprite_rect.colliderect(down_rect):
                return sprite
        return None

    def horizontal_collide(self):
        if self.direction.x > 0:  # moving right
            sprite = self.sprite_right_collide()
            if sprite:
                self.hitbox.right = sprite.hitbox.left
        elif self.direction.x < 0:  # moving left
            sprite = self.sprite_left_collide()
            if sprite:
                self.hitbox.left = sprite.hitbox.right

    def vertical_collide(self):
        if self.direction.y > 0:  # moving down
            sprite = self.sprite_down_collide()
            if sprite:
                self.hitbox.bottom = sprite.hitbox.top
                self.direction.y = 0
        elif self.direction.y < 0:  # moving up
            sprite = self.sprite_up_collide()
            if sprite:
                self.hitbox.top = sprite.hitbox.bottom
                self.direction.y = 0

    def take_damage(self, damage):
        if not self.invulnerability_timer.active:
            self.health -= damage
            print(f"Player took {damage} damage. Health: {self.health}")
            if self.health <= 0:
                print("Player died.")
            else:
                self.invulnerability_timer.activate()
                self.direction.y = DAMAGE_FORCE

    def flicker_alpha_value(self):
        if sin(pygame.time.get_ticks()) > 0:
            return 255
        else:
            return 0

    def make_invulnerable(self):
        self.image.set_alpha(self.flicker_alpha_value())

    def make_vulnerable(self):
        self.image.set_alpha(255)

    def update_timers(self):
        self.invulnerability_timer.update()

    def update(self, dt):
        self.check_on_floor()
        if not self.on_floor:
            self.apply_gravity(dt)
        self.input()
        self.update_orientation()
        self.move(dt)
        self.update_status()
        super().update(dt)
        if self.invulnerability_timer.active:
            self.invulnerability_timer.update()
            self.make_invulnerable()
        else:
            self.make_vulnerable()
