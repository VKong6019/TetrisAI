from collections import defaultdict

import pygame
import numpy as np
# from GeneticTetris import GeneticTetris
from models.Tetris import Tetris
from GreedyTetris import bfs
from AStarTetris import aStarSearch


colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

WIDTH = 400
HEIGHT = 500
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)

action_seq = []
while not done:
    ######################################################################
    # this is where we modify to include AI work

    if game.figure is None:
        game.new_figure()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                game.go_down()
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_ESCAPE:
                game.__init__(20, 10)
    
        if game.state != "gameover":
            print(action_seq)
            if len(action_seq) > 0:
                action = action_seq.pop()
                if action == "right":
                    game.go_side(1)
                elif action == "left":
                    game.go_side(-1)
                elif action == "down":
                    game.go_down()
                elif action == "space":
                    game.go_space()
                elif action == "rotate":
                    game.rotate()
                else:
                    game.go_default()
            else:
                game.get_string_field()
                # AI heuristics
                # action_seq = aStarSearch(game)
                # action_seq = GeneticTetris.getBestMove(game)

    # end of revision
    ######################################################################

    screen.fill(WHITE)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                    [game.x + game.zoom * (j + game.figure.x) + 1,
                                    game.y + game.zoom * (i + game.figure.y) + 1,
                                    game.zoom - 2, game.zoom - 2])

    font = pygame.font.SysFont('comicsans', 25, True, False)
    font1 = pygame.font.SysFont('comicsans', 70, True, False)
    text = font.render("Score: " + str(game.score), True, BLACK)
    text_game_over = font1.render("Game Over!", True, (250, 125, 125))

    screen.blit(text, [10, 10])
    if game.state == "gameover":
        screen.blit(text_game_over, [50, 200])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
