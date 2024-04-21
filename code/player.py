import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, animations=[], status="idle_right"):
        super().__init__(groups)
        self.position = position
        self.animations = animations
        self.status = status
        self.frame_index = 0
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=self.position)
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

    def move(self, dt):
        self.position += self.direction * self.speed * dt
        self.rect.topleft = (round(self.position.x), round(self.position.y))

    def update(self, dt):
        self.input()
        self.move(dt)
