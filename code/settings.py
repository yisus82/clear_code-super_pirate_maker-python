# general setup
FPS = 60
TILE_SIZE = 64
ANIMATION_SPEED = 8
PLAYER_SPEED = 300
GRAVITY = 4
JUMP_FORCE = -2
PLAYER_HITBOX_OFFSET = (-50, 0)
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
TERRAIN_TYPES = {
    "land": {
        "animated": False,
    },
    "water": {
        "animated": True,
    },
}
COLLECTABLE_TYPES = {
    "coin": {
        "gold": {
            "value": 5,
        },
        "silver": {
            "value": 1,
        },
        "diamond": {
            "value": 10,
        },
    },
}
ENEMY_TYPES = {
    "spikes": [],
    "tooth": [],
    "shell": ["left", "right"],
}
PARTICLE_TYPES = ["coin"]
PALM_TYPES = ["small", "large", "left", "right"]
FOREGROUND_TYPES = {
    "palm fg": {
        "types": {
            "small": {
                "mask_offset": (0, 0),
                "mask_size": (75, 50),
            },
            "large": {
                "mask_offset": (0, 0),
                "mask_size": (75, 50),
            },
            "left": {
                "mask_offset": (0, 0),
                "mask_size": (75, 50),
            },
            "right": {
                "mask_offset": (50, 0),
                "mask_size": (75, 50),
            },
        },
    },
}
BACKGROUND_TYPES = {
    "palm bg": PALM_TYPES,
}
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
