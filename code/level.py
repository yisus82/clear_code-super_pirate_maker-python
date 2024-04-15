import sys

import pygame


class Level:
    def __init__(self, grid, switch_mode):
        self.display_surface = pygame.display.get_surface()
        self.grid = grid
        self.switch_mode = switch_mode

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # switch to the editor
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch_mode()

    def run(self, dt):
        self.event_loop()
        self.display_surface.fill("red")
