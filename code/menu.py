from os import path

import pygame
from button import Button
from settings import (BUTTON_LINE_COLOR, COIN_TYPES, ENEMY_TYPES,
                      MENU_BUTTON_MARGIN, MENU_MARGIN, MENU_SIZE, PALM_TYPES,
                      TERRAIN_DATA)


class Menu:
  def __init__(self):
    self.display_surface = pygame.display.get_surface()
    self.menu_items = []
    self.load_menu_items()
    self.menu_surfaces = {}
    self.create_menu_surfaces()
    self.rect = pygame.Rect((self.display_surface.get_width() - MENU_SIZE - MENU_MARGIN, 
                             self.display_surface.get_height() - MENU_SIZE - MENU_MARGIN), 
                             (MENU_SIZE, MENU_SIZE))
    self.menu_buttons = pygame.sprite.Group()
    self.menu_buttons_rects = {}
    self.create_buttons()
    
  def load_menu_items(self):
    # terrain
    for key in TERRAIN_DATA.keys():
      self.menu_items.append(f"terrain_{key}")
    # coins
    for value in COIN_TYPES:
      self.menu_items.append(f"coin_{value}")
    # enemies
    for value in ENEMY_TYPES:
      self.menu_items.append(f"enemy_{value}")
    # palms foreground
    for value in PALM_TYPES:
      self.menu_items.append(f"palm fg_{value}")
    # palms background
    for value in PALM_TYPES:
      self.menu_items.append(f"palm bg_{value}")

  def create_menu_surfaces(self):
    for index, item in enumerate(self.menu_items):
      menu_section = item.split("_")[0].replace(" ", "_")
      menu_item = item.split("_")[1].replace(" ", "_")
      menu_surface_path = path.join("..", "graphics", "menu", menu_section, f"{menu_item}.png")
      if menu_section in self.menu_surfaces:
        self.menu_surfaces[menu_section].append((index, pygame.image.load(menu_surface_path)))
      else:
        self.menu_surfaces[menu_section] = [(index, pygame.image.load(menu_surface_path))]

  def create_buttons(self):
    # button areas
    generic_button_rect = pygame.Rect(self.rect.topleft, (self.rect.width / 2, self.rect.height / 2))
    terrain_button_rect = generic_button_rect.copy().inflate(-MENU_BUTTON_MARGIN, -MENU_BUTTON_MARGIN)
    coin_button_rect = generic_button_rect.move(self.rect.height / 2, 0).inflate(-MENU_BUTTON_MARGIN, -MENU_BUTTON_MARGIN)
    enemy_button_rect = generic_button_rect.move(0, self.rect.width / 2).inflate(-MENU_BUTTON_MARGIN, -MENU_BUTTON_MARGIN)
    palm_button_rect = generic_button_rect.move(self.rect.height / 2, self.rect.width / 2).inflate(-MENU_BUTTON_MARGIN, -MENU_BUTTON_MARGIN)
    self.menu_buttons_rects["terrain"] = terrain_button_rect
    self.menu_buttons_rects["coin"] = coin_button_rect
    self.menu_buttons_rects["enemy"] = enemy_button_rect
    self.menu_buttons_rects["palm_fg"] = palm_button_rect
    self.menu_buttons_rects["palm_bg"] = palm_button_rect

    # create the buttons
    Button(terrain_button_rect, self.menu_buttons, self.menu_surfaces["terrain"])
    Button(coin_button_rect, self.menu_buttons, self.menu_surfaces["coin"])
    Button(enemy_button_rect, self.menu_buttons, self.menu_surfaces["enemy"])
    Button(palm_button_rect, self.menu_buttons, self.menu_surfaces["palm_fg"] + self.menu_surfaces["palm_bg"])

  def click(self, mouse_pos, mouse_button):
    for menu_button in self.menu_buttons:
      if menu_button.rect.collidepoint(mouse_pos):
        # right click
        if mouse_button[2]: 
          menu_button.switch_item()
        return menu_button.get_menu_item_index()

  def update_selected_item(self, index):
    menu_item = self.menu_items[index]
    menu_section = menu_item.split("_")[0].replace(" ", "_")
    pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.menu_buttons_rects[menu_section].inflate(10, 10), 5, 0)
    for menu_button in self.menu_buttons:
      for item in menu_button.items:
        if item[0] == index:
          menu_button.select_item(index)

  def display(self, index):
    self.update_selected_item(index)
    self.menu_buttons.update()
    self.menu_buttons.draw(self.display_surface)
