import pygame
from settings import BUTTON_BG_COLOR


class Button(pygame.sprite.Sprite):
    def __init__(self, rect, groups, items):
        super().__init__(groups)
        self.rect = rect
        self.image = pygame.Surface(self.rect.size)
        self.items = items
        self.selected_index = 0

    def select_item(self, index):
        for i in range(0, len(self.items)):
            if self.items[i][0] == index:
                self.selected_index = i
                break

    def get_menu_item_index(self):
        return self.items[self.selected_index][0]

    def switch_item(self):
        self.selected_index = (self.selected_index + 1) % len(self.items)

    def update(self):
        self.image.fill(BUTTON_BG_COLOR)
        surface = self.items[self.selected_index][1]
        rect = surface.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(surface, rect)
