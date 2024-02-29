import sys

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

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick(FPS) / 1000
            self.editor.run(dt)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()