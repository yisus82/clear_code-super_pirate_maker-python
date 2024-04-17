import sys

import pygame
import pygame_gui
from player import Player
from settings import SKY_COLOR
from sprites import Generic


class Level:
    def __init__(self, ui_manager, grid, switch_mode, assets):
        # main setup
        self.display_surface = pygame.display.get_surface()
        self.ui_manager = ui_manager
        self.grid = grid
        self.switch_mode = switch_mode

        # assets setup
        self.assets = assets
        self.all_sprites = pygame.sprite.Group()
        self.player = None
        self.build_level()

    def build_level(self):
        # player
        position, status = list(self.grid["player"].items())[0]
        self.player = Player(
            position, [self.all_sprites], self.assets["player"], status
        )

        # land
        for position, land_tile_type in self.grid["land"].items():
            surface = self.assets["land"][land_tile_type]
            Generic(position, surface, [self.all_sprites])

    def process_event(self, event):
        # gui events
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_object_id == "exit":
                pygame.quit()
                sys.exit()
            elif event.ui_object_id == "switch_mode":
                self.switch_mode()
        if self.ui_manager.opened_dialog:
            return

        # quit the game
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            self.confirm_exit()

        # switch to the editor
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.confirm_switch_mode()

    def confirm_exit(self):
        self.ui_manager.show_confirmation_dialog(
            "Exit",
            "Are you sure you want to exit the application?",
            "Exit",
            "exit",
        )

    def confirm_switch_mode(self):
        self.ui_manager.show_confirmation_dialog(
            "Switch mode",
            "Are you sure you want to switch to the game?",
            "Switch",
            "switch_mode",
        )

    def update(self, dt):
        self.display_surface.fill(SKY_COLOR)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)
        self.ui_manager.display()
