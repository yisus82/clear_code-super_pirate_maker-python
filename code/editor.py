import ast
import datetime
import sys
from os import path
from random import choice, randint

import pygame
import pygame_gui
from canvas_object import CanvasObject, PlayerObject, SkyHandle
from canvas_tile import CanvasTile
from menu import Menu
from settings import (
    ANIMATION_SPEED,
    HORIZON_COLOR,
    HOVER_COLOR,
    HOVER_INFLATE_OFFSET,
    HOVER_SIZE,
    HOVER_WIDTH,
    INITIAL_CLOUDS_CENTER,
    INITIAL_CLOUDS_LEFT,
    INITIAL_CLOUDS_RIGHT,
    LINE_COLOR,
    NEIGHBOR_DIRECTIONS,
    SEA_COLOR,
    SKY_COLOR,
    TILE_SIZE,
)
from timer import Timer
from utils import import_folder


class Editor:
    def __init__(self, ui_manager, land_tile_types, switch_mode):
        # main setup
        self.display_surface = pygame.display.get_surface()
        self.window_width = self.display_surface.get_width()
        self.window_height = self.display_surface.get_height()
        self.ui_manager = ui_manager
        self.switch_mode = switch_mode

        # menu setup
        self.menu = Menu()
        self.selected_index = 0

        # assets setup
        self.canvas_data = {}
        self.land_tile_types = land_tile_types
        self.water_bottom = pygame.image.load(
            path.join("..", "graphics", "terrain", "water", "water_bottom.png")
        ).convert_alpha()
        self.animations = {}
        self.import_animations()
        self.frame_index = 0
        self.preview_surfaces = {}
        self.import_preview_surfaces()

        # clouds setup
        self.current_clouds = []
        clouds_path = path.join("..", "graphics", "clouds", "small")
        self.cloud_surfaces = import_folder(clouds_path)
        self.cloud_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.create_initial_clouds()

        # navigation setup
        self.origin = pygame.Vector2(0, 0)
        self.pan_active = False
        self.pan_offset = pygame.Vector2(0, 0)
        self.pan_timer = Timer(200)

        # support line setup
        self.support_line_surface = pygame.Surface(
            (self.window_width, self.window_height), pygame.SRCALPHA
        )
        self.support_line_surface.set_colorkey("green")
        self.support_line_surface.set_alpha(30)

        # objects
        self.canvas_objects = pygame.sprite.Group()
        self.foreground_objects = pygame.sprite.Group()
        self.background_objects = pygame.sprite.Group()
        self.object_drag_active = False
        self.object_timer = Timer(400)

        # player
        player_path = path.join("..", "graphics", "player", "idle_right")
        self.player_animations = import_folder(player_path)
        self.player = PlayerObject(
            (200, self.window_height / 2),
            self.player_animations,
            self.origin,
            [self.canvas_objects, self.foreground_objects],
        )

        # sky
        sky_handle_path = path.join("..", "graphics", "cursors", "handle.png")
        self.sky_handle_surf = pygame.image.load(sky_handle_path).convert_alpha()
        self.sky_handle = SkyHandle(
            (self.window_width / 2, self.window_height / 2),
            [self.sky_handle_surf],
            self.origin,
            [self.canvas_objects, self.foreground_objects],
        )

    def process_event(self, event):
        # gui events
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            self.import_grid(event.text)
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_object_id == "export":
                self.export_grid()
            elif event.ui_object_id == "exit":
                pygame.quit()
                sys.exit()
            elif event.ui_object_id == "switch_mode":
                self.switch_mode(self.create_grid())
        if self.ui_manager.opened_dialog:
            return

        # quit the game
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            self.confirm_exit()

        # reset the origin
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            self.origin = pygame.Vector2(0, 0)

        # switch to the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.confirm_switch_mode()

        # export the grid
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.confirm_export()

        # import the grid
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.ui_manager.prompt_file()

        # editor events
        self.create_clouds(event)
        self.pan_input(event)
        self.selection_hotkeys(event)
        self.menu_click(event)
        self.object_drag(event)
        self.canvas_click(event)

    def import_animations(self):
        for index, item in enumerate(self.menu.menu_items):
            menu_section = item.split("_")[0].replace(" ", "_")
            menu_item = item.split("_")[1].replace(" ", "_")
            menu_item_folder = path.join(
                "..", "graphics", menu_section, menu_item, "idle"
            )
            self.animations[index] = import_folder(menu_item_folder)

    def import_preview_surfaces(self):
        for index, item in enumerate(self.menu.menu_items):
            menu_section = item.split("_")[0].replace(" ", "_")
            menu_item = item.split("_")[1].replace(" ", "_")
            menu_item_path = path.join(
                "..", "graphics", "preview", menu_section, f"{menu_item}.png"
            )
            menu_item_surface = pygame.image.load(menu_item_path).convert_alpha()
            self.preview_surfaces[index] = (menu_section, menu_item_surface)

    def create_grid(self):
        # clear the objects from the tiles
        for tile in self.canvas_data.values():
            tile.objects = []

        # add objects to the tiles
        for obj in self.canvas_objects:
            cell = self.get_cell(obj.distance_to_origin)
            offset = pygame.Vector2(obj.distance_to_origin) - (
                pygame.Vector2(cell) * TILE_SIZE
            )
            if cell in self.canvas_data:
                self.canvas_data[cell].add_item(
                    obj.item_type, obj.item_id, offset, obj.background
                )
            else:
                self.canvas_data[cell] = CanvasTile(
                    obj.item_type, obj.item_id, offset, obj.background
                )

        # create an empty grid
        layers = {
            "player": {},
            "sky_handle": {},
            "water": {},
            "land": {},
            "coin": {},
            "enemy": {},
            "foreground": {},
            "background": {},
        }

        # fill the grid
        for tile_pos, tile in self.canvas_data.items():
            x = tile_pos[0] * TILE_SIZE
            y = tile_pos[1] * TILE_SIZE

            if tile.has_water:
                layers["water"][(x, y)] = tile.get_water_position()

            if tile.has_land:
                layers["land"][(x, y)] = (
                    tile.get_land_tile_type()
                    if tile.get_land_tile_type() in self.land_tile_types
                    else "X"
                )

            if tile.coin:
                layers["coin"][(x + TILE_SIZE // 2, y + TILE_SIZE // 2)] = (
                    self.menu.get_menu_item(tile.coin)[1]
                )

            if tile.enemy:
                layers["enemy"][x, y] = self.menu.get_menu_item(tile.enemy)[1]

            for item_type, item_id, offset in tile.foreground_objects:
                if item_type == "player":
                    layers["player"][(int(x + offset.x), int(y + offset.y))] = (
                        "idle_right"
                    )
                elif item_type == "sky_handle":
                    layers["sky_handle"][(int(x + offset.x), int(y + offset.y))] = (
                        "sky_handle"
                    )
                else:
                    layers["foreground"][(int(x + offset.x), int(y + offset.y))] = (
                        self.menu.get_menu_item(item_id)
                    )

            for item_type, item_id, offset in tile.background_objects:
                layers["background"][(int(x + offset.x), int(y + offset.y))] = (
                    self.menu.get_menu_item(item_id)
                )

        return layers

    def confirm_export(self):
        self.ui_manager.show_confirmation_dialog(
            "Export grid...",
            "The grid will be saved as a text file in the 'levels' folder.",
            "Export",
            "export",
        )

    def export_success(self, file_name):
        self.ui_manager.show_information_dialog(
            "Export success",
            f"The grid was successfully exported as <b>{file_name}</b> in the 'levels' folder.",
        )

    def export_grid(self):
        grid = self.create_grid()
        save_path = path.join("..", "levels")
        current_date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = path.join(save_path, f"level_{current_date_time}.txt")
        with open(file_name, "x") as file:
            file.write(str(grid))
        self.export_success(f"level_{current_date_time}.txt")

    def import_grid(self, file_name):
        if not file_name:
            self.prompt_file()
        else:
            with open(file_name, "r") as file:
                grid = file.read()
                try:
                    grid_dict = ast.literal_eval(grid)
                except (
                    ValueError,
                    TypeError,
                    SyntaxError,
                    MemoryError,
                    RecursionError,
                ):
                    self.ui_manager.show_information_dialog(
                        "Error", "Invalid grid format"
                    )
                    return

                if (
                    grid_dict is None
                    or not isinstance(grid_dict, dict)
                    or not grid_dict["player"]
                    or not isinstance(grid_dict["player"], dict)
                    or len(grid_dict["player"].items()) != 1
                    or not grid_dict["sky_handle"]
                    or not isinstance(grid_dict["sky_handle"], dict)
                    or len(grid_dict["sky_handle"].items()) != 1
                ):
                    self.ui_manager.show_information_dialog(
                        "Error", "Invalid grid format"
                    )
                    return

                # save originally placed objects
                original_origin = self.origin
                original_player = self.player
                original_sky_handle = self.sky_handle
                original_canvas_data = self.canvas_data.copy()
                original_objects = self.canvas_objects.copy()
                original_background_objects = self.background_objects.copy()
                original_foreground_objects = self.foreground_objects.copy()

                # reset origin
                self.origin = pygame.Vector2(0, 0)

                # clear the canvas
                self.canvas_data.clear()
                self.canvas_objects.empty()
                self.background_objects.empty()
                self.foreground_objects.empty()

                try:
                    # player
                    position = list(grid_dict["player"].keys())[0]
                    self.player = PlayerObject(
                        position,
                        self.player_animations,
                        self.origin,
                        [self.canvas_objects, self.foreground_objects],
                        False,
                    )

                    # sky handle
                    position = list(grid_dict["sky_handle"].keys())[0]
                    self.sky_handle = SkyHandle(
                        position,
                        [self.sky_handle_surf],
                        self.origin,
                        [self.canvas_objects, self.foreground_objects],
                        False,
                    )

                    # water
                    if grid_dict["water"]:
                        if not isinstance(grid_dict["water"], dict):
                            raise ValueError
                        for position in grid_dict["water"].keys():
                            cell = self.get_cell(position)
                            if cell not in self.canvas_data:
                                self.canvas_data[cell] = CanvasTile(
                                    "water",
                                    self.menu.get_menu_item_index("terrain", "water"),
                                )
                            else:
                                self.canvas_data[cell].add_item(
                                    "water",
                                    self.menu.get_menu_item_index("terrain", "water"),
                                )
                            self.check_neighbors(cell)

                    # land
                    if grid_dict["land"]:
                        if not isinstance(grid_dict["land"], dict):
                            raise ValueError
                        for position in grid_dict["land"].keys():
                            cell = self.get_cell(position)
                            if cell not in self.canvas_data:
                                self.canvas_data[cell] = CanvasTile(
                                    "land",
                                    self.menu.get_menu_item_index("terrain", "land"),
                                )
                            else:
                                self.canvas_data[cell].add_item(
                                    "land",
                                    self.menu.get_menu_item_index("terrain", "land"),
                                )
                            self.check_neighbors(cell)

                    # coin
                    if grid_dict["coin"]:
                        if not isinstance(grid_dict["coin"], dict):
                            raise ValueError
                        for position, item_id in grid_dict["coin"].items():
                            cell = self.get_cell(position)
                            if cell not in self.canvas_data:
                                self.canvas_data[cell] = CanvasTile(
                                    "coin",
                                    self.menu.get_menu_item_index("coin", item_id),
                                )
                            else:
                                self.canvas_data[cell].add_item(
                                    "coin",
                                    self.menu.get_menu_item_index("coin", item_id),
                                )

                    # enemy
                    if grid_dict["enemy"]:
                        if not isinstance(grid_dict["enemy"], dict):
                            raise ValueError
                        for position, item_id in grid_dict["enemy"].items():
                            cell = self.get_cell(position)
                            if cell not in self.canvas_data:
                                self.canvas_data[cell] = CanvasTile(
                                    "enemy",
                                    self.menu.get_menu_item_index("enemy", item_id),
                                )
                            else:
                                self.canvas_data[cell].add_item(
                                    "enemy",
                                    self.menu.get_menu_item_index("enemy", item_id),
                                )

                    # foreground
                    if grid_dict["foreground"]:
                        if not isinstance(grid_dict["foreground"], dict):
                            raise ValueError
                        for position, item in grid_dict["foreground"].items():
                            menu_section, menu_item = item
                            item_id = self.menu.get_menu_item_index(
                                menu_section, menu_item
                            )
                            CanvasObject(
                                position,
                                self.animations[item_id],
                                self.origin,
                                [self.canvas_objects, self.foreground_objects],
                                menu_section,
                                item_id,
                                False,
                                False,
                            )

                    # background
                    if grid_dict["background"]:
                        if not isinstance(grid_dict["background"], dict):
                            raise ValueError
                        for position, item in grid_dict["background"].items():
                            menu_section, menu_item = item
                            item_id = self.menu.get_menu_item_index(
                                menu_section, menu_item
                            )
                            CanvasObject(
                                position,
                                self.animations[item_id],
                                self.origin,
                                [self.canvas_objects, self.background_objects],
                                menu_section,
                                item_id,
                                True,
                                False,
                            )
                except Exception:
                    self.ui_manager.show_information_dialog(
                        "Error", "Invalid grid format"
                    )
                    self.origin = original_origin
                    self.player = original_player
                    self.sky_handle = original_sky_handle
                    self.canvas_data = original_canvas_data
                    self.canvas_objects = original_objects
                    self.background_objects = original_background_objects
                    self.foreground_objects = original_foreground_objects

    def toggle_pan(self):
        self.pan_active = not self.pan_active
        if self.pan_active:
            self.pan_offset = pygame.Vector2(pygame.mouse.get_pos()) - self.origin

    def pan_input(self, event):
        # mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.origin.x -= event.y * 50
            else:
                self.origin.y -= event.y * 50
            for sprite in self.canvas_objects:
                sprite.update_position(self.origin)

        # panning
        if pygame.key.get_pressed()[pygame.K_p] and not self.pan_timer.active:
            self.toggle_pan()
            self.pan_timer.activate()
        if self.pan_active:
            self.origin = pygame.Vector2(pygame.mouse.get_pos()) - self.pan_offset
            for sprite in self.canvas_objects:
                sprite.update_position(self.origin)

    def selection_hotkeys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(
                    self.menu.menu_items
                )
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(
                    self.menu.menu_items
                )

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            self.selected_index = self.menu.click(
                pygame.mouse.get_pos(), pygame.mouse.get_pressed()
            )

    def object_drag(self, event):
        # start dragging
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(event.pos):
                    sprite.start_drag()
                    self.object_drag_active = True

        # stop dragging
        if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            for sprite in self.canvas_objects:
                if sprite.selected:
                    sprite.drag_end(self.origin)
                    self.object_drag_active = False

    def check_neighbors(self, cell_pos):
        # create a local cluster
        cluster_size = 3
        local_cluster = [
            (
                cell_pos[0] + col - int(cluster_size / 2),
                cell_pos[1] + row - int(cluster_size / 2),
            )
            for col in range(cluster_size)
            for row in range(cluster_size)
        ]

        # check neighbors
        for cell in local_cluster:
            if cell in self.canvas_data:
                self.canvas_data[cell].land_neighbors = []
                self.canvas_data[cell].water_bottom = False
                for name, offset in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + offset[0], cell[1] + offset[1])
                    if neighbor_cell in self.canvas_data:
                        # water neighbors
                        if (
                            name == "A"
                            and self.canvas_data[cell].has_water
                            and self.canvas_data[neighbor_cell].has_water
                        ):
                            self.canvas_data[cell].water_bottom = True

                        # land neighbors
                        if self.canvas_data[neighbor_cell].has_land:
                            self.canvas_data[cell].land_neighbors.append(name)

    def get_cell(self, pos):
        return (pos[0] - int(self.origin.x)) // TILE_SIZE, (
            pos[1] - int(self.origin.y)
        ) // TILE_SIZE

    def canvas_click(self, event):
        if self.object_drag_active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN or (
            pygame.key.get_pressed()[pygame.K_LSHIFT] and pygame.mouse.get_pressed()[0]
        ):
            mouse_pos = pygame.mouse.get_pos()
            if not self.menu.rect.collidepoint(mouse_pos):
                cell = self.get_cell(mouse_pos)
                # left click (add items)
                if pygame.mouse.get_pressed()[0]:
                    item_type = (
                        self.menu.menu_items[self.selected_index]
                        .split("_")[0]
                        .replace(" ", "_")
                    )
                    # tiles
                    if item_type in ("terrain", "coin", "enemy"):
                        if item_type == "terrain":
                            item_type = (
                                self.menu.menu_items[self.selected_index]
                                .split("_")[1]
                                .replace(" ", "_")
                            )
                        if cell not in self.canvas_data:
                            self.canvas_data[cell] = CanvasTile(
                                item_type, self.selected_index
                            )
                        else:
                            self.canvas_data[cell].add_item(
                                item_type, self.selected_index
                            )
                        self.check_neighbors(cell)
                    # objects
                    else:
                        if not self.object_timer.active:
                            background = True if item_type == "palm_bg" else False
                            groups = (
                                [self.canvas_objects, self.background_objects]
                                if background
                                else [self.canvas_objects, self.foreground_objects]
                            )
                            CanvasObject(
                                mouse_pos,
                                self.animations[self.selected_index],
                                self.origin,
                                groups,
                                item_type,
                                self.selected_index,
                                background,
                            )
                            self.object_timer.activate()
                # right click (delete items)
                elif pygame.mouse.get_pressed()[2]:
                    # tiles
                    if cell in self.canvas_data:
                        del self.canvas_data[cell]
                        self.check_neighbors(cell)

                    # objects
                    for sprite in self.canvas_objects:
                        # player and sky handle are not deletable
                        if isinstance(sprite, PlayerObject) or isinstance(
                            sprite, SkyHandle
                        ):
                            continue
                        if sprite.rect.collidepoint(mouse_pos):
                            sprite.kill()

    def draw_tile_lines(self):
        cols = self.display_surface.get_width() // TILE_SIZE
        rows = self.display_surface.get_height() // TILE_SIZE
        origin_offset = pygame.Vector2(
            self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
            self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE,
        )
        self.support_line_surface.fill("green")
        for col in range(cols + 1):
            x = origin_offset.x + col * TILE_SIZE
            pygame.draw.line(
                self.support_line_surface,
                LINE_COLOR,
                (x, 0),
                (x, self.display_surface.get_height()),
            )
        for row in range(rows + 1):
            y = origin_offset.y + row * TILE_SIZE
            pygame.draw.line(
                self.support_line_surface,
                LINE_COLOR,
                (0, y),
                (self.display_surface.get_width(), y),
            )
        self.display_surface.blit(self.support_line_surface, (0, 0))

    def get_position(self, cell):
        return cell[0] * TILE_SIZE + self.origin.x, cell[1] * TILE_SIZE + self.origin.y

    def draw_level(self):
        # background objects
        self.background_objects.draw(self.display_surface)

        # tiles
        for cell, tile in self.canvas_data.items():
            pos = self.get_position(cell)

            # water
            if tile.has_water:
                if tile.water_bottom:
                    self.display_surface.blit(self.water_bottom, pos)
                else:
                    frames = self.animations[1]
                    frame = int(self.frame_index % len(frames))
                    surface = frames[frame]
                    self.display_surface.blit(surface, pos)

            # land
            if tile.has_land:
                land_type = "".join(tile.land_neighbors)
                surface = (
                    self.land_tile_types[land_type]
                    if land_type in self.land_tile_types
                    else self.land_tile_types["X"]
                )
                self.display_surface.blit(surface, pos)

            # coin
            if tile.coin is not None:
                frames = self.animations[tile.coin]
                frame = int(self.frame_index % len(frames))
                surface = frames[frame]
                rect = surface.get_rect(
                    center=(pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE // 2)
                )
                self.display_surface.blit(surface, rect)

            # enemy
            if tile.enemy is not None:
                frames = self.animations[tile.enemy]
                frame = int(self.frame_index % len(frames))
                surface = frames[frame]
                rect = surface.get_rect(
                    midbottom=(pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE)
                )
                self.display_surface.blit(surface, rect)

        # foreground objects
        self.foreground_objects.draw(self.display_surface)

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos):
                rect = sprite.rect.inflate(HOVER_INFLATE_OFFSET)
                pygame.draw.lines(
                    self.display_surface,
                    HOVER_COLOR,
                    False,
                    (
                        (rect.left, rect.top + HOVER_SIZE),
                        rect.topleft,
                        (rect.left + HOVER_SIZE, rect.top),
                    ),
                    HOVER_WIDTH,
                )
                pygame.draw.lines(
                    self.display_surface,
                    HOVER_COLOR,
                    False,
                    (
                        (rect.right - HOVER_SIZE, rect.top),
                        rect.topright,
                        (rect.right, rect.top + HOVER_SIZE),
                    ),
                    HOVER_WIDTH,
                )
                pygame.draw.lines(
                    self.display_surface,
                    HOVER_COLOR,
                    False,
                    (
                        (rect.right - HOVER_SIZE, rect.bottom),
                        rect.bottomright,
                        (rect.right, rect.bottom - HOVER_SIZE),
                    ),
                    HOVER_WIDTH,
                )
                pygame.draw.lines(
                    self.display_surface,
                    HOVER_COLOR,
                    False,
                    (
                        (rect.left, rect.bottom - HOVER_SIZE),
                        rect.bottomleft,
                        (rect.left + HOVER_SIZE, rect.bottom),
                    ),
                    HOVER_WIDTH,
                )

    def preview(self):
        mouse_pos = pygame.mouse.get_pos()
        if not self.menu.rect.collidepoint(mouse_pos):
            menu_section, menu_item_surface = self.preview_surfaces[self.selected_index]
            surface = menu_item_surface.copy()
            surface.set_alpha(100)

            # tile
            if menu_section in ("terrain", "coin", "enemy"):
                cell = self.get_cell(mouse_pos)
                rect = surface.get_rect(
                    topleft=self.origin + pygame.Vector2(cell) * TILE_SIZE
                )
            # object
            else:
                rect = surface.get_rect(center=mouse_pos)

            self.display_surface.blit(surface, rect)

    def draw_background(self):
        horizon_y = self.sky_handle.rect.centery
        if horizon_y > 0:
            # sky and clouds
            self.display_surface.fill(SKY_COLOR)
            self.draw_clouds(horizon_y)

            if horizon_y < self.window_height:
                # sea and horizon line
                sea_rect = pygame.Rect(
                    0, horizon_y, self.window_width, self.window_height
                )
                pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
                pygame.draw.line(
                    self.display_surface,
                    HORIZON_COLOR,
                    (0, horizon_y),
                    (self.window_width, horizon_y),
                    3,
                )
        else:
            # only sea
            self.display_surface.fill(SEA_COLOR)

    def draw_clouds(self, horizon_y):
        for cloud in self.current_clouds:
            x = cloud["position"][0] + self.origin.x
            y = horizon_y - cloud["position"][1]
            self.display_surface.blit(cloud["surface"], (x, y))

    def create_cloud(self, position="right"):
        surface = choice(self.cloud_surfaces)
        if randint(0, 4) < 2:
            surface = pygame.transform.scale2x(surface)
        if position == "center":
            x_position = randint(0, self.window_width)
        elif position == "right":
            x_position = randint(self.window_width, self.window_width * 2)
        else:
            x_position = randint(-self.window_width, 0)
        position = [x_position, randint(0, self.window_height)]
        return {"surface": surface, "position": position, "speed": randint(20, 50)}

    def create_clouds(self, event):
        if event.type == self.cloud_timer:
            self.current_clouds.append(self.create_cloud())

    def create_initial_clouds(self):
        for _ in range(INITIAL_CLOUDS_LEFT):
            self.current_clouds.append(self.create_cloud("left"))
        for _ in range(INITIAL_CLOUDS_CENTER):
            self.current_clouds.append(self.create_cloud("center"))
        for _ in range(INITIAL_CLOUDS_RIGHT):
            self.current_clouds.append(self.create_cloud("right"))

    def update_clouds(self, dt):
        # move clouds
        for cloud in self.current_clouds:
            cloud["position"][0] -= cloud["speed"] * dt

        # remove clouds that are out of the screen
        self.current_clouds = [
            cloud
            for cloud in self.current_clouds
            if cloud["position"][0] > -self.window_width
        ]

    def draw_world_limits(self):
        x_min = -self.window_width + self.origin.x
        x_max = 2 * self.window_width + self.origin.x
        y_min = -self.window_height + self.origin.y
        y_max = 2 * self.window_height + self.origin.y
        rect = pygame.Rect(x_min, y_min, x_max - x_min, y_max - y_min)
        pygame.draw.rect(self.display_surface, "red", rect, 3)

    def update_timers(self):
        self.pan_timer.update()
        self.object_timer.update()

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
        self.frame_index += ANIMATION_SPEED * dt
        self.canvas_objects.update(dt)
        self.update_clouds(dt)
        self.update_timers()
        self.display_surface.fill("gray")
        self.draw_background()
        self.draw_level()
        self.draw_tile_lines()
        pygame.draw.circle(self.display_surface, "red", self.origin, 10)
        self.draw_world_limits()
        self.preview()
        self.hover()
        self.menu.display(self.selected_index)
        self.ui_manager.display()
