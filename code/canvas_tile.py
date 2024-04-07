class CanvasTile:
    def __init__(self, item_type, item_id):
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

        self.add_item(item_type, item_id)

    def add_item(self, item_type, item_id):
        match item_type:
            case "land":
                self.has_land = True
            case "water":
                self.has_water = True
            case "coin":
                self.coin = item_id
            case "enemy":
                self.enemy = item_id

    def __str__(self):
        return f"CanvasTile(land: {self.has_land}, water: {self.has_water}, coin: {self.coin}, enemy: {self.enemy})"
