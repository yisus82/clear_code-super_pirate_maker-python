from os import path

import pygame
from editor import Editor
from settings import FPS
from utils import import_folder_as_dict


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("Super Pirate Maker")
        self.clock = pygame.time.Clock()
        self.land_tiles = self.import_land_tiles()
        self.editor = Editor(self.land_tiles)
        mouse_path = path.join("..", "graphics", "cursors", "mouse.png")
        mouse_surface = pygame.image.load(mouse_path).convert_alpha()
        self.mouse_cursor = pygame.cursors.Cursor((0, 0), mouse_surface)

    def import_land_tiles(self):
        return import_folder_as_dict(path.join("..", "graphics", "terrain", "land"))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.editor.run(dt)
            pygame.mouse.set_cursor(self.mouse_cursor)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
