from os import path

import pygame
from editor import Editor
from level import Level
from settings import FPS
from transition import Transition
from utils import import_folder_as_dict


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("Super Pirate Maker")
        self.clock = pygame.time.Clock()
        self.land_tile_types = self.import_land_tile_types()
        self.editor_active = True
        self.transition = Transition(self.toggle_editor)
        self.editor = Editor(self.land_tile_types, self.switch_mode)
        self.level = None
        mouse_path = path.join("..", "graphics", "cursors", "mouse.png")
        mouse_surface = pygame.image.load(mouse_path).convert_alpha()
        self.mouse_cursor = pygame.cursors.Cursor((0, 0), mouse_surface)

    def import_land_tile_types(self):
        return import_folder_as_dict(path.join("..", "graphics", "terrain", "land"))

    def toggle_editor(self):
        self.editor_active = not self.editor_active

    def switch_mode(self, grid=None):
        self.transition.active = True
        if grid:
            self.level = Level(grid, self.switch_mode)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            if self.editor_active:
                pygame.mouse.set_cursor(self.mouse_cursor)
                pygame.mouse.set_visible(True)
                self.editor.run(dt)
            else:
                pygame.mouse.set_visible(False)
                self.level.run(dt)
            self.transition.display(dt)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
