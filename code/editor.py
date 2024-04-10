import sys
from os import path

import pygame
from canvas_object import CanvasObject, PlayerObject, SkyHandle
from canvas_tile import CanvasTile
from menu import Menu
from settings import (
    ANIMATION_SPEED,
    HOVER_COLOR,
    HOVER_INFLATE_OFFSET,
    HOVER_SIZE,
    HOVER_WIDTH,
    LINE_COLOR,
    NEIGHBOR_DIRECTIONS,
    TILE_SIZE,
)
from timer import Timer
from utils import import_folder


class Editor:
    def __init__(self, land_tiles):
        # display setup
        self.display_surface = pygame.display.get_surface()
        self.window_width = self.display_surface.get_width()
        self.window_height = self.display_surface.get_height()

        # menu setup
        self.menu = Menu()
        self.selected_index = 0

        # assets setup
        self.canvas_data = {}
        self.land_tiles = land_tiles
        self.water_bottom = pygame.image.load(
            path.join("..", "graphics", "terrain", "water", "water_bottom.png")
        ).convert_alpha()
        self.animations = {}
        self.import_animations()
        self.frame_index = 0
        self.preview_surfaces = {}
        self.import_preview_surfaces()

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
        self.object_drag_active = False
        self.object_timer = Timer(400)

        # player
        player_path = path.join("..", "graphics", "player", "idle_right")
        self.player_animations = import_folder(player_path)
        PlayerObject(
            (200, self.window_height / 2),
            self.player_animations,
            self.origin,
            [self.canvas_objects],
        )

        # sky
        sky_handle_path = path.join("..", "graphics", "cursors", "handle.png")
        self.sky_handle_surf = pygame.image.load(sky_handle_path).convert_alpha()
        self.sky_handle = SkyHandle(
            (self.window_width / 2, self.window_height / 2),
            [self.sky_handle_surf],
            self.origin,
            [self.canvas_objects],
        )

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

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.object_drag(event)
            self.canvas_click(event)

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

        # panning
        if pygame.key.get_pressed()[pygame.K_p] and not self.pan_timer.active:
            self.toggle_pan()
            self.pan_timer.activate()
        if self.pan_active:
            self.origin = pygame.Vector2(pygame.mouse.get_pos()) - self.pan_offset

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
                current_cell = self.get_cell(mouse_pos)
                # left click (add items)
                if pygame.mouse.get_pressed()[0]:
                    item_type = self.menu.menu_items[self.selected_index].split("_")[0]
                    # tiles
                    if item_type in ("terrain", "coin", "enemy"):
                        if item_type == "terrain":
                            item_type = self.menu.menu_items[self.selected_index].split(
                                "_"
                            )[1]
                        if current_cell not in self.canvas_data:
                            self.canvas_data[current_cell] = CanvasTile(
                                item_type, self.selected_index
                            )
                        else:
                            self.canvas_data[current_cell].add_item(
                                item_type, self.selected_index
                            )
                        self.check_neighbors(current_cell)
                    # objects
                    else:
                        if not self.object_timer.active:
                            CanvasObject(
                                mouse_pos,
                                self.animations[self.selected_index],
                                self.selected_index,
                                self.origin,
                                [self.canvas_objects],
                            )
                            self.object_timer.activate()
                # right click (delete items)
                elif pygame.mouse.get_pressed()[2]:
                    # tiles
                    if current_cell in self.canvas_data:
                        del self.canvas_data[current_cell]
                        self.check_neighbors(current_cell)

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
        # objects
        self.canvas_objects.draw(self.display_surface)

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
                    self.land_tiles[land_type]
                    if land_type in self.land_tiles
                    else self.land_tiles["X"]
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
                current_cell = self.get_cell(mouse_pos)
                rect = surface.get_rect(
                    topleft=self.origin + pygame.Vector2(current_cell) * TILE_SIZE
                )
            # object
            else:
                rect = surface.get_rect(center=mouse_pos)

            self.display_surface.blit(surface, rect)

    def update_timers(self):
        self.pan_timer.update()
        self.object_timer.update()

    def run(self, dt):
        self.event_loop()
        self.frame_index += ANIMATION_SPEED * dt
        self.canvas_objects.update(dt)
        self.update_timers()
        self.display_surface.fill("gray")
        self.draw_level()
        self.draw_tile_lines()
        pygame.draw.circle(self.display_surface, "red", self.origin, 10)
        self.preview()
        self.hover()
        self.menu.display(self.selected_index)
