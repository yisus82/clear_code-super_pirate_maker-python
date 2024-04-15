import pygame
from settings import ANIMATION_SPEED


class CanvasObject(pygame.sprite.Sprite):
    def __init__(self, pos, frames, origin, groups, item_type="object", item_id=None):
        super().__init__(groups)
        self.item_type = item_type
        self.item_id = item_id

        # animation
        self.frames = frames
        self.frame_index = 0

        # image
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # movement
        self.distance_to_origin = pygame.Vector2(self.rect.topleft) - origin
        self.selected = False
        self.mouse_offset = pygame.Vector2()

    def start_drag(self):
        self.selected = True
        self.mouse_offset = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(
            self.rect.topleft
        )

    def drag(self):
        if self.selected:
            self.rect.topleft = pygame.mouse.get_pos() - self.mouse_offset

    def drag_end(self, origin):
        self.selected = False
        self.distance_to_origin = pygame.Vector2(self.rect.topleft) - origin

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        frame = int(self.frame_index % len(self.frames))
        self.image = self.frames[frame]
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def update_position(self, origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self, dt):
        self.animate(dt)
        self.drag()


class PlayerObject(CanvasObject):
    def __init__(self, pos, frames, origin, groups):
        super().__init__(pos, frames, origin, groups, "player")


class SkyHandle(CanvasObject):
    def __init__(self, pos, frames, origin, groups):
        super().__init__(pos, frames, origin, groups, "sky_handle")
