import sys

import pygame
from menu import Menu
from settings import LINE_COLOR, TILE_SIZE
from timer import Timer


class Editor:
  def __init__(self):
    # display setup
    self.display_surface = pygame.display.get_surface()
    self.window_width = self.display_surface.get_width()
    self.window_height = self.display_surface.get_height()

    # navigation setup
    self.origin = pygame.Vector2(0, 0)
    self.pan_active = False
    self.pan_offset = pygame.Vector2(0, 0)
    self.pan_timer = Timer(200)

    # support line setup
    self.support_line_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
    self.support_line_surface.set_colorkey("green")
    self.support_line_surface.set_alpha(30)

    # menu setup
    self.menu = Menu()
    self.selected_index = 0

  def event_loop(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
          pygame.quit()
          sys.exit()
      self.pan_input(event)
      self.selection_hotkeys(event)
      self.menu_click(event)

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
        self.selected_index = (self.selected_index + 1) % len(self.menu.items)
      if event.key == pygame.K_LEFT:
        self.selected_index = (self.selected_index - 1) % len(self.menu.items)

  def menu_click(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(pygame.mouse.get_pos()):
      self.selected_index = self.menu.click(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

  def draw_tile_lines(self):
    cols = self.display_surface.get_width() // TILE_SIZE
    rows = self.display_surface.get_height()// TILE_SIZE
    origin_offset = pygame.Vector2(self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE, 
                                   self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE)
    self.support_line_surface.fill("green")
    for col in range(cols + 1):
      x = origin_offset.x + col * TILE_SIZE
      pygame.draw.line(self.support_line_surface, LINE_COLOR, (x, 0), (x, self.display_surface.get_height()))
    for row in range(rows + 1):
      y = origin_offset.y + row * TILE_SIZE
      pygame.draw.line(self.support_line_surface, LINE_COLOR, (0, y), (self.display_surface.get_width(), y))
    self.display_surface.blit(self.support_line_surface, (0, 0))

  def update_timers(self):
    self.pan_timer.update()

  def run(self, dt):
    self.event_loop()
    self.update_timers()
    self.display_surface.fill("white")
    self.draw_tile_lines()
    pygame.draw.circle(self.display_surface, "red", self.origin, 10)
    self.menu.display(self.selected_index)
    