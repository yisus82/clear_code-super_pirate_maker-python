import pygame
from settings import GRAVITY, JUMP_FORCE, PLAYER_HITBOX_OFFSET, PLAYER_SPEED
from sprites import Animated


class Player(Animated):
    def __init__(
        self, position, animations, groups, collision_sprites, status="idle_right"
    ):
        super().__init__(position, animations, groups, status, pivot="bottomleft")
        self.collision_sprites = collision_sprites
        self.speed = PLAYER_SPEED
        self.on_floor = False
        self.direction = pygame.Vector2()
        self.orientation = self.status.split("_")[1]
        self.hitbox = self.rect.inflate(*PLAYER_HITBOX_OFFSET)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
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
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 10))
        for sprite in self.collision_sprites:
            sprite_rect = pygame.Rect(sprite.hitbox.topleft, (sprite.hitbox.width, 10))
            if sprite_rect.colliderect(floor_rect):
                self.on_floor = True
                self.hitbox.bottom = sprite.hitbox.top
                self.direction.y = 0
                return
        self.on_floor = False

    def horizontal_collide(self):
        if self.direction.x > 0:  # moving right
            right_rect = pygame.Rect(self.hitbox.topright, (10, self.hitbox.height))
            for sprite in self.collision_sprites:
                sprite_rect = pygame.Rect(
                    sprite.hitbox.topleft, (10, sprite.hitbox.height)
                )
                if sprite_rect.colliderect(right_rect):
                    self.hitbox.right = sprite.hitbox.left
        elif self.direction.x < 0:  # moving left
            left_rect = pygame.Rect(self.hitbox.topleft, (10, self.hitbox.height))
            for sprite in self.collision_sprites:
                sprite_rect = pygame.Rect(
                    sprite.hitbox.topright, (10, sprite.hitbox.height)
                )
                if sprite_rect.colliderect(left_rect):
                    self.hitbox.left = sprite.hitbox.right

    def vertical_collide(self):
        if self.direction.y > 0:  # moving down
            bottom_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 10))
            for sprite in self.collision_sprites:
                sprite_rect = pygame.Rect(
                    sprite.hitbox.topleft, (sprite.hitbox.width, 10)
                )
                if sprite_rect.colliderect(bottom_rect):
                    self.hitbox.bottom = sprite.hitbox.top
                    self.direction.y = 0
        elif self.direction.y < 0:  # moving up
            top_rect = pygame.Rect(self.hitbox.topleft, (self.hitbox.width, 10))
            for sprite in self.collision_sprites:
                sprite_rect = pygame.Rect(
                    sprite.hitbox.bottomleft, (sprite.hitbox.width, 10)
                )
                if sprite_rect.colliderect(top_rect):
                    self.hitbox.top = sprite.hitbox.bottom
                    self.direction.y = 0

    def update(self, dt):
        self.check_on_floor()
        if not self.on_floor:
            self.apply_gravity(dt)
        self.input()
        self.update_orientation()
        self.move(dt)
        self.update_status()
        super().update(dt)
