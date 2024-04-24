import pygame
from settings import SORTING_LAYERS


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def custom_draw(self, player):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.offset.x = player.rect.centerx - window_width / 2
        self.offset.y = player.rect.centery - window_height / 2

        for layer in SORTING_LAYERS:
            for sprite in self.sprites():
                if sprite.sorting_layer == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
