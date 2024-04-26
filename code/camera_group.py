import pygame
from settings import HORIZON_COLOR, HORIZON_TOP_COLOR, SEA_COLOR, SORTING_LAYERS


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw_horizon(self, horizon_y):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        horizon_pos = horizon_y - self.offset.y

        if horizon_pos < window_height:
            sea_rect = pygame.Rect(
                0, horizon_pos, window_width, window_height - horizon_pos
            )
            pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
            horizon_rect1 = pygame.Rect(0, horizon_pos - 10, window_width, 10)
            horizon_rect2 = pygame.Rect(0, horizon_pos - 16, window_width, 4)
            horizon_rect3 = pygame.Rect(0, horizon_pos - 20, window_width, 2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)
            pygame.draw.line(
                self.display_surface,
                HORIZON_COLOR,
                (0, horizon_pos),
                (window_width, horizon_pos),
                3,
            )

        if horizon_pos < 0:
            self.display_surface.fill(SEA_COLOR)

    def custom_draw(self, player, horizon_y):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.offset.x = player.rect.centerx - window_width / 2
        self.offset.y = player.rect.centery - window_height / 2

        self.draw_horizon(horizon_y)

        for layer in SORTING_LAYERS:
            for sprite in self.sprites():
                if sprite.sorting_layer == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
