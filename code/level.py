import sys
from os import path
from random import choice, randint

import pygame
import pygame_gui
from camera_group import CameraGroup
from enemy import Enemy, Shell, Spikes, Tooth
from player import Player
from settings import (
    COLLECTABLE_TYPES,
    FOREGROUND_TYPES,
    INITIAL_CLOUDS_LEVEL,
    SKY_COLOR,
)
from sprites import AnimatedObject, Cloud, Coin, Generic, Mask, Particle, Water


class Level:
    def __init__(self, ui_manager, grid, assets, switch_mode, reset_level, debug=False):
        # main setup
        self.display_surface = pygame.display.get_surface()
        self.ui_manager = ui_manager
        self.grid = grid
        self.switch_mode = switch_mode
        self.paused = False
        self.debug = debug
        self.reset_level = reset_level

        # assets setup
        self.assets = assets
        self.all_sprites = CameraGroup()
        self.animated_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.player = None
        self.horizon_y = self.display_surface.get_height() // 2
        self.build_level()
        self.right_edge = sorted(
            list(self.grid["land"].keys()), key=lambda pos: pos[0]
        )[-1][0]
        self.cloud_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.create_initial_clouds()
        level_sound_path = path.join("..", "audio", "level.ogg")
        self.level_sound = pygame.mixer.Sound(level_sound_path)
        self.level_sound.set_volume(0.4)
        self.level_sound.play(loops=-1)

    def build_level(self):
        # player
        position, status = list(self.grid["player"].items())[0]
        self.player = Player(
            position,
            self.assets["player"],
            [self.all_sprites, self.animated_sprites],
            self.collision_sprites,
            status,
        )

        # horizon
        self.horizon_y = list(self.grid["sky_handle"].keys())[0][1]

        # land
        if "land" in self.grid:
            for position, land_tile_type in self.grid["land"].items():
                surface = self.assets["land"][land_tile_type]
                Generic(position, surface, [self.all_sprites, self.collision_sprites])

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
                    Generic(
                        position,
                        self.assets["water_bottom"],
                        [self.all_sprites],
                        sorting_layer="water",
                    )

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
                if enemy_type == "spikes":
                    Spikes(
                        position,
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.damage_sprites,
                        ],
                        self.assets["enemy"][enemy_type],
                    )
                elif enemy_type == "tooth":
                    Tooth(
                        position,
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.damage_sprites,
                        ],
                        self.assets["enemy"][enemy_type],
                        collision_sprites=self.collision_sprites,
                    )
                elif enemy_type == "shell_left":
                    Shell(
                        position,
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.collision_sprites,
                        ],
                        self.assets["enemy"]["shell"],
                        self.assets["pearl"],
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.damage_sprites,
                        ],
                        self.player,
                        "left",
                    )
                elif enemy_type == "shell_right":
                    Shell(
                        position,
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.collision_sprites,
                        ],
                        self.assets["enemy"]["shell"],
                        self.assets["pearl"],
                        [
                            self.all_sprites,
                            self.animated_sprites,
                            self.enemy_sprites,
                            self.damage_sprites,
                        ],
                        self.player,
                        "right",
                    )
                else:
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
                object_type = foreground_object_type.replace("_", " ")
                object_subtype = foreground_object_subtype.replace("_", " ")
                if FOREGROUND_TYPES[object_type]["types"]:
                    mask_offset = FOREGROUND_TYPES[object_type]["types"][
                        object_subtype
                    ]["mask_offset"]
                    mask_size = FOREGROUND_TYPES[object_type]["types"][object_subtype][
                        "mask_size"
                    ]
                    Mask(
                        position + pygame.Vector2(mask_offset),
                        mask_size,
                        [self.collision_sprites],
                    )
                else:
                    mask_offset = FOREGROUND_TYPES[object_type]["mask_offset"]
                    mask_size = FOREGROUND_TYPES[object_type]["mask_size"]
                    Mask(
                        position + pygame.Vector2(mask_offset),
                        mask_size,
                        [self.collision_sprites],
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
                    background=True,
                    sorting_layer="background",
                )

    def process_event(self, event):
        # gui events
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_object_id == "exit":
                pygame.quit()
                sys.exit()
            elif event.ui_object_id == "switch_mode":
                self.switch_mode()
            elif event.ui_object_id == "try_again":
                self.reset_level(self.grid)
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

        # pause the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.toggle_pause()

        # create a cloud
        if event.type == self.cloud_timer:
            self.create_cloud()

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.level_sound.play(loops=-1)
        else:
            self.paused = True
            self.level_sound.stop()

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

    def confirm_game_over(self):
        self.ui_manager.show_confirmation_dialog(
            "Game over",
            "You died. Do you want to try again?",
            "Try again",
            "try_again",
        )

    def confirm_win(self):
        self.ui_manager.show_confirmation_dialog(
            "You win",
            "You completed the level. Do you want to play again?",
            "Play again",
            "try_again",
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
                sprite.play_sound()
                coin_value = COLLECTABLE_TYPES["coin"][sprite.coin_type]["value"]
                print(f"Player collected a {sprite.coin_type} coin worth {coin_value}.")
        if self.collectable_sprites.sprites() == []:
            print("All collectables collected.")
            self.toggle_pause()
            self.confirm_win()

    def check_damage(self):
        for sprite in pygame.sprite.spritecollide(
            self.player, self.damage_sprites, False, pygame.sprite.collide_mask
        ):
            sprite.damage_player(self.player)
            if self.player.health <= 0:
                self.player.kill()
                self.toggle_pause()
                self.confirm_game_over()

    def create_cloud(self, offscreen=True):
        left_limit = -self.display_surface.get_width()
        right_limit = self.right_edge + 500
        surface = choice(self.assets["cloud"])
        if randint(0, 5) > 3:
            surface = pygame.transform.scale2x(surface)
        x = (
            right_limit + randint(100, 300)
            if offscreen
            else randint(left_limit, right_limit)
        )
        y = self.horizon_y - randint(100, 600)
        Cloud(
            (x, y),
            surface,
            [self.all_sprites, self.animated_sprites],
            left_limit,
            randint(75, 125),
        )

    def create_initial_clouds(self):
        for _ in range(INITIAL_CLOUDS_LEVEL):
            self.create_cloud(offscreen=False)

    def update(self, dt):
        self.display_surface.fill(SKY_COLOR)
        if not self.paused:
            self.get_collectables()
            self.check_damage()
            self.animated_sprites.update(dt)
        self.all_sprites.custom_draw(self.player, self.horizon_y)
        if self.debug:
            for sprite in self.collision_sprites:
                sprite.draw_hitbox(self.display_surface, self.player)
        if self.paused:
            dark_surface = pygame.Surface(self.display_surface.get_size())
            dark_surface.set_alpha(128)
            dark_surface.fill((0, 0, 0))
            self.display_surface.blit(dark_surface, (0, 0))
        self.ui_manager.display()
