import pygame


class CanvasTile:
    def __init__(self, item_type, item_id, offset=pygame.Vector2(), background=False):
        # land
        self.has_land = False
        self.land_neighbors = []

        # water
        self.has_water = False
        self.water_bottom = False

        # coin
        self.coin = None

        # enemy
        self.enemy = None

        # background objects
        self.background_objects = []

        # foreground objects
        self.foreground_objects = []

        self.add_item(item_type, item_id, offset, background)

    def add_item(self, item_type, item_id, offset=pygame.Vector2(), background=False):
        match item_type:
            case "land":
                self.has_land = True
            case "water":
                self.has_water = True
            case "coin":
                self.coin = item_id
            case "enemy":
                self.enemy = item_id
            # objects
            case _:
                if background:
                    if (item_type, item_id, offset) not in self.background_objects:
                        self.background_objects.append((item_type, item_id, offset))
                else:
                    if (item_type, item_id, offset) not in self.foreground_objects:
                        self.foreground_objects.append((item_type, item_id, offset))

    def get_water_position(self):
        return "bottom" if self.water_bottom else "top"

    def get_land_tile_type(self):
        return "".join(self.land_neighbors)

    def __str__(self):
        return f"land: {self.has_land}, water: {self.has_water}, coin: {self.coin}, enemy: {self.enemy}, bg: {self.background_objects}, fg: {self.foreground_objects}"
