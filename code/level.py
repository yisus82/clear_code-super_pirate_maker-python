import sys

import pygame
import pygame_gui
from enemy import Enemy
from player import Player
from settings import COLLECTABLE_TYPES, SKY_COLOR
from sprites import AnimatedObject, Coin, Generic, Particle, Water


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
        self.animated_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.player = None
        self.build_level()

    def build_level(self):
        # player
        position, status = list(self.grid["player"].items())[0]
        self.player = Player(
            position,
            [self.all_sprites, self.animated_sprites],
            self.assets["player"],
            status,
        )

        # land
        if "land" in self.grid:
            for position, land_tile_type in self.grid["land"].items():
                surface = self.assets["land"][land_tile_type]
                Generic(position, surface, [self.all_sprites])

        # water
        if "water" in self.grid:
            for position, water_type in self.grid["water"].items():
                if water_type == "top":
                    Water(
                        water_type,
                        position,
                        self.assets["water_top"],
                        [self.all_sprites, self.animated_sprites],
                    )
                elif water_type == "bottom":
                    Generic(position, self.assets["water_bottom"], [self.all_sprites])

        # coins
        if "coin" in self.grid:
            for position, coin_type in self.grid["coin"].items():
                Coin(
                    coin_type,
                    position,
                    self.assets["coin"][coin_type],
                    [self.all_sprites, self.animated_sprites, self.collectable_sprites],
                )

        # enemies
        if "enemy" in self.grid:
            for position, enemy_type in self.grid["enemy"].items():
                Enemy(
                    enemy_type,
                    position,
                    [self.all_sprites, self.animated_sprites, self.enemy_sprites],
                    self.assets["enemy"][enemy_type],
                )

        # foreground objects
        if "foreground" in self.grid:
            for position, foreground_object in self.grid["foreground"].items():
                foreground_object_type, foreground_object_subtype = foreground_object
                AnimatedObject(
                    foreground_object_type,
                    foreground_object_subtype,
                    position,
                    self.assets["foreground"][foreground_object_type][
                        foreground_object_subtype
                    ]
                    if foreground_object_subtype
                    else self.assets["foreground"][foreground_object_type],
                    [self.all_sprites, self.animated_sprites],
                )

        # background objects
        if "background" in self.grid:
            for position, background_object in self.grid["background"].items():
                background_object_type, background_object_subtype = background_object
                AnimatedObject(
                    background_object_type,
                    background_object_subtype,
                    position,
                    self.assets["background"][background_object_type][
                        background_object_subtype
                    ]
                    if background_object_subtype
                    else self.assets["background"][background_object_type],
                    [self.all_sprites, self.animated_sprites],
                )

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

    def get_collectables(self):
        collided_collectables = pygame.sprite.spritecollide(
            self.player, self.collectable_sprites, True
        )
        for sprite in collided_collectables:
            if isinstance(sprite, Coin):
                Particle(
                    sprite.rect.center,
                    self.assets["particle"]["coin"],
                    [self.all_sprites, self.animated_sprites],
                    500,
                )
                coin_value = COLLECTABLE_TYPES["coin"][sprite.coin_type]["value"]
                print(f"Player collected a {sprite.coin_type} coin worth {coin_value}.")

    def update(self, dt):
        self.display_surface.fill(SKY_COLOR)
        self.get_collectables()
        self.animated_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)
        self.ui_manager.display()
