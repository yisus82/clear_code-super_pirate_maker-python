# general setup
FPS = 60
TILE_SIZE = 64
ANIMATION_SPEED = 8
INITIAL_CLOUDS_CENTER = 20
INITIAL_CLOUDS_RIGHT = 10
INITIAL_CLOUDS_LEFT = 50

# colors
BUTTON_BG_COLOR = "#33323d"
BUTTON_LINE_COLOR = "gold"
HORIZON_COLOR = "#f5f1de"
HOVER_COLOR = "black"
LINE_COLOR = "black"
SEA_COLOR = "#92a9ce"
SKY_COLOR = "#ddc6a1"

# editor items
TERRAIN_DATA = {
    "land": {
        "animated": False,
    },
    "water": {
        "animated": True,
    },
}
COIN_TYPES = ["gold", "silver", "diamond"]
ENEMY_TYPES = ["spikes", "tooth", "shell left", "shell right"]
PALM_TYPES = ["small", "large", "left", "right"]
NEIGHBOR_DIRECTIONS = {
    "A": (0, -1),
    "B": (1, -1),
    "C": (1, 0),
    "D": (1, 1),
    "E": (0, 1),
    "F": (-1, 1),
    "G": (-1, 0),
    "H": (-1, -1),
}

# menu
MENU_SIZE = 180
MENU_MARGIN = 6
MENU_BUTTON_MARGIN = 5

# hover
HOVER_INFLATE_OFFSET = (10, 10)
HOVER_WIDTH = 3
HOVER_SIZE = 15
