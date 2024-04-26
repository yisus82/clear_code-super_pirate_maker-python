from os import path

import pygame
from editor import Editor
from level import Level
from settings import (
    BACKGROUND_TYPES,
    COLLECTABLE_TYPES,
    ENEMY_TYPES,
    FOREGROUND_TYPES,
    FPS,
    PARTICLE_TYPES,
)
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
        mouse_path = path.join("..", "graphics", "cursor", "mouse.png")
        mouse_surface = pygame.image.load(mouse_path).convert_alpha()
        self.mouse_cursor = pygame.cursors.Cursor((0, 0), mouse_surface)
        self.debug = False

    def import_assets(self):
        # land
        land_path = path.join("..", "graphics", "terrain", "land")
        self.assets["land"] = import_folder_as_dict(land_path)

        # player
        player_path = path.join("..", "graphics", "player")
        self.assets["player"] = import_subfolders_as_list(player_path)

        # water
        water_bottom_path = path.join(
            "..", "graphics", "terrain", "water", "water_bottom.png"
        )
        self.assets["water_bottom"] = pygame.image.load(
            water_bottom_path
        ).convert_alpha()
        water_top_path = path.join("..", "graphics", "terrain", "water")
        self.assets["water_top"] = import_subfolders_as_list(water_top_path)

        # coin
        self.assets["coin"] = {}
        for value in COLLECTABLE_TYPES["coin"].keys():
            coin_type = value.replace(" ", "_")
            coin_path = path.join("..", "graphics", "coin", coin_type)
            self.assets["coin"][coin_type] = import_subfolders_as_list(coin_path)

        # enemy
        self.assets["enemy"] = {}
        for value in ENEMY_TYPES.keys():
            enemy_type = value.replace(" ", "_")
            enemy_path = path.join("..", "graphics", "enemy", enemy_type)
            self.assets["enemy"][enemy_type] = import_subfolders_as_list(enemy_path)

        # foreground
        self.assets["foreground"] = {}
        for main_type, values in FOREGROUND_TYPES.items():
            foreground_type = main_type.replace(" ", "_")
            foreground_path = path.join("..", "graphics", foreground_type)
            if values["types"]:
                self.assets["foreground"][foreground_type] = {}
                subtypes = values["types"].keys()
                for subtype in subtypes:
                    subtype_path = path.join(foreground_path, subtype)
                    self.assets["foreground"][foreground_type][subtype] = (
                        import_subfolders_as_list(subtype_path)
                    )
            else:
                self.assets["foreground"][foreground_type] = import_subfolders_as_list(
                    foreground_path
                )

        # background
        self.assets["background"] = {}
        for main_type, subtypes in BACKGROUND_TYPES.items():
            background_type = main_type.replace(" ", "_")
            background_path = path.join("..", "graphics", background_type)
            if len(subtypes) > 0:
                self.assets["background"][background_type] = {}
                for subtype in subtypes:
                    subtype_path = path.join(background_path, subtype)
                    self.assets["background"][background_type][subtype] = (
                        import_subfolders_as_list(subtype_path)
                    )
            else:
                self.assets["background"][background_type] = import_subfolders_as_list(
                    background_path
                )

        # particles
        self.assets["particle"] = {}
        for value in PARTICLE_TYPES:
            particle_type = value.replace(" ", "_")
            particle_path = path.join("..", "graphics", "particle", particle_type)
            self.assets["particle"][particle_type] = import_subfolders_as_list(
                particle_path
            )

        # pearl
        pearl_path = path.join("..", "graphics", "pearl", "pearl.png")
        self.assets["pearl"] = pygame.image.load(pearl_path).convert_alpha()

    def toggle_editor(self):
        self.editor_active = not self.editor_active

    def switch_mode(self, grid=None):
        self.transition.active = True
        if grid:
            self.level = Level(
                self.ui_manager, grid, self.switch_mode, self.assets, self.debug
            )

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
