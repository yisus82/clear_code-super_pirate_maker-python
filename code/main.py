from os import path

import pygame
from editor import Editor
from settings import FPS


class Game:
  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    pygame.display.set_caption("Super Pirate Maker")
    self.clock = pygame.time.Clock()
    self.editor = Editor()
    mouse_path = path.join("..", "graphics", "cursors", "mouse.png")
    mouse_surface = pygame.image.load(mouse_path).convert_alpha()
    mouse_cursor = pygame.cursors.Cursor((0,0), mouse_surface)
    pygame.mouse.set_cursor(mouse_cursor)

  def run(self):
    while True:
      dt = self.clock.tick(FPS) / 1000
      self.editor.run(dt)
      pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
