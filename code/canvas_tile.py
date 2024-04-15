import pygame


class CanvasTile:
    def __init__(self, item_type, item_id, offset=pygame.Vector2()):
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

        # objects
        self.objects = []

        self.add_item(item_type, item_id, offset)

    def add_item(self, item_type, item_id, offset=pygame.Vector2()):
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
                if (item_type, item_id, offset) not in self.objects:
                    self.objects.append((item_type, item_id, offset))

    def get_water_position(self):
        return "bottom" if self.water_bottom else "top"

    def get_land_tile_type(self):
        return "".join(self.land_neighbors)

    def __str__(self):
        return f"land: {self.has_land}, water: {self.has_water}, coin: {self.coin}, enemy: {self.enemy}, objects: {self.objects}"
