# general setup
FPS = 60
TILE_SIZE = 64

# colors
LINE_COLOR = "black"
BUTTON_BG_COLOR = "#33323d"
BUTTON_LINE_COLOR = "gold"

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
