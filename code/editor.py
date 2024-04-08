import sys
from os import path

import pygame
from canvas_tile import CanvasTile
from menu import Menu
from settings import ANIMATION_SPEED, LINE_COLOR, NEIGHBOR_DIRECTIONS, TILE_SIZE
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
        )
        self.animations = {}
        self.import_animations()
        self.frame_index = 0

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

    def import_animations(self):
        for index, item in enumerate(self.menu.menu_items):
            menu_section = item.split("_")[0].replace(" ", "_")
            menu_item = item.split("_")[1].replace(" ", "_")
            menu_item_folder = path.join(
                "..", "graphics", menu_section, menu_item, "idle"
            )
            self.animations[index] = import_folder(menu_item_folder)

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
        if event.type == pygame.MOUSEBUTTONDOWN or (
            pygame.key.get_pressed()[pygame.K_LSHIFT] and pygame.mouse.get_pressed()[0]
        ):
            mouse_pos = pygame.mouse.get_pos()
            if not self.menu.rect.collidepoint(mouse_pos):
                current_cell = self.get_cell(mouse_pos)
                # left click
                if pygame.mouse.get_pressed()[0]:
                    item_type = self.menu.menu_items[self.selected_index].split("_")[0]
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
                # right click
                elif pygame.mouse.get_pressed()[2]:
                    if current_cell in self.canvas_data:
                        del self.canvas_data[current_cell]
                self.check_neighbors(current_cell)

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

            # objects
            for obj in tile.objects:
                pygame.draw.rect(
                    self.display_surface,
                    "black",
                    pygame.Rect(pos, (TILE_SIZE, TILE_SIZE)),
                )

    def update_timers(self):
        self.pan_timer.update()

    def run(self, dt):
        self.event_loop()
        self.frame_index += ANIMATION_SPEED * dt
        self.update_timers()
        self.display_surface.fill("gray")
        self.draw_level()
        self.draw_tile_lines()
        pygame.draw.circle(self.display_surface, "red", self.origin, 10)
        self.menu.display(self.selected_index)
