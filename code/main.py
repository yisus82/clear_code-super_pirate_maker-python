from os import path

import pygame
from editor import Editor
from level import Level
from settings import COIN_TYPES, FPS
from transition import Transition
from ui_manager import UIManager
from utils import import_folder_as_dict, import_subfolders_as_list


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption("Super Pirate Maker")
        self.clock = pygame.time.Clock()
        self.assets = {}
        self.import_assets()
        self.editor_active = True
        self.transition = Transition(self.toggle_editor)
        self.ui_manager = UIManager()
        self.editor = Editor(self.ui_manager, self.assets["land"], self.switch_mode)
        self.level = None
        mouse_path = path.join("..", "graphics", "cursors", "mouse.png")
        mouse_surface = pygame.image.load(mouse_path).convert_alpha()
        self.mouse_cursor = pygame.cursors.Cursor((0, 0), mouse_surface)

    def import_assets(self):
        land_path = path.join("..", "graphics", "terrain", "land")
        self.assets["land"] = import_folder_as_dict(land_path)
        player_path = path.join("..", "graphics", "player")
        self.assets["player"] = import_subfolders_as_list(player_path)
        water_bottom_path = path.join(
            "..", "graphics", "terrain", "water", "water_bottom.png"
        )
        self.assets["water_bottom"] = pygame.image.load(
            water_bottom_path
        ).convert_alpha()
        water_top_path = path.join("..", "graphics", "terrain", "water")
        self.assets["water_top"] = import_subfolders_as_list(water_top_path)
        self.assets["coin"] = {}
        for value in COIN_TYPES:
            coin_path = path.join("..", "graphics", "coin", value)
            self.assets["coin"][value] = import_subfolders_as_list(coin_path)

    def toggle_editor(self):
        self.editor_active = not self.editor_active

    def switch_mode(self, grid=None):
        self.transition.active = True
        if grid:
            self.level = Level(self.ui_manager, grid, self.switch_mode, self.assets)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self.ui_manager.process_event(event)
                if self.editor_active:
                    self.editor.process_event(event)
                else:
                    self.level.process_event(event)
            if self.editor_active:
                pygame.mouse.set_cursor(self.mouse_cursor)
                pygame.mouse.set_visible(True)
                self.ui_manager.update(dt)
                self.editor.update(dt)
            else:
                pygame.mouse.set_visible(False)
                self.ui_manager.update(dt)
                if self.ui_manager.opened_dialog:
                    pygame.mouse.set_cursor(self.mouse_cursor)
                    pygame.mouse.set_visible(True)
                self.level.update(dt)
            if self.transition.active:
                self.transition.update(dt)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
