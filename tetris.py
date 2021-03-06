import pygame
import time
from models.Tetris import Tetris
from GeneticTetris import Genetics
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

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

WIDTH = 400
HEIGHT = 500
size = (WIDTH, HEIGHT)
fps = 25


class TetrisGame():
    def __init__(self):
        # Initialize the self.game engine
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.font = pygame.font.SysFont('comicsans', 25, True, False)
        self.font1 = pygame.font.SysFont('comicsans', 70, True, False)
        pygame.display.set_caption("Tetris")
        self.reset_game()
        self.action_seq = []

    def display_game_over(self):
        text_game_over = self.font1.render("Game Over!", True, (250, 125, 125))
        self.screen.blit(text_game_over, [0, 200])

    # start game over
    def reset_game(self):
        self.game = Tetris(20, 10)
        self.game.get_string_field()
        # Loop until the user clicks the close button.
        self.isGameOver = False
        self.clock = pygame.time.Clock()

    def run_game(self):
        while not self.isGameOver:
            if self.game.figure is None:
                self.game.new_figure()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isGameOver = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.game.rotate()
                    if event.key == pygame.K_DOWN:
                        self.game.go_down()
                    if event.key == pygame.K_LEFT:
                        self.game.go_side(-1)
                    if event.key == pygame.K_RIGHT:
                        self.game.go_side(1)
                    if event.key == pygame.K_SPACE:
                        self.game.go_space()
                    if event.key == pygame.K_ESCAPE:
                        self.game.__init__(20, 10)

                if self.game.state != "gameover":
                    genetics = Genetics()
                    best_state = genetics.genetics(self)

                if len(self.action_seq) > 0:
                    action = self.action_seq.pop()
                    if action == "right":
                        self.game.go_side(1)
                    elif action == "left":
                        self.game.go_side(-1)
                    elif action == "down":
                        self.game.go_down()
                    elif action == "space":
                        self.game.go_space()
                    elif action == "rotate":
                        self.game.rotate()
                    else:
                        self.game.go_default()
                else:
                    # self.game.get_string_field()
                    # AI heuristics
                    # print("CALLED!")
                    # action_seq = genetics.state.game.get_best_state(genetics.weights)[2]
                    # time.sleep(2)
                    # print("I AM HERE")
                    # time.sleep(5)
                    print(self.action_seq)
                self.game.moves += 1

            self.display()

            if self.game.state == "gameover":
                self.display_game_over()
                return self.game.get_score()

            pygame.display.flip()
            self.clock.tick(fps)

        pygame.quit()

    def run_astar_or_greedy(self, runAStar):
        done = False
        while not done:
            if self.game.figure is None:
                self.game.new_figure()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            if self.game.state != "gameover":
                if len(self.action_seq) > 0:
                    action = self.action_seq.pop()
                    if action == "right":
                        self.game.go_side(1)
                    elif action == "left":
                        self.game.go_side(-1)
                    elif action == "down":
                        self.game.go_down()
                    elif action == "space":
                        self.game.go_space()
                    elif action == "rotate":
                        self.game.rotate()
                    else:
                        self.game.go_default()
                else:
                    self.action_seq = aStarSearch(self.game) if runAStar else bfs(self.game)

            self.display()

            if self.game.state == "gameover":
                self.display_game_over()

            pygame.display.flip()
            self.clock.tick(fps)

        pygame.quit()

    def display(self):
        self.screen.fill(WHITE)

        for i in range(self.game.height):
            for j in range(self.game.width):
                pygame.draw.rect(self.screen, GRAY,
                                 [self.game.x + self.game.zoom * j, self.game.y + self.game.zoom * i, self.game.zoom,
                                  self.game.zoom], 1)
                if self.game.field[i][j] > 0:
                    pygame.draw.rect(self.screen, colors[self.game.field[i][j]],
                                     [self.game.x + self.game.zoom * j + 1, self.game.y + self.game.zoom * i + 1,
                                      self.game.zoom - 2,
                                      self.game.zoom - 1])

        if self.game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.figure.image():
                        pygame.draw.rect(self.screen, colors[self.game.figure.color],
                                         [self.game.x + self.game.zoom * (j + self.game.figure.x) + 1,
                                          self.game.y + self.game.zoom * (i + self.game.figure.y) + 1,
                                          self.game.zoom - 2, self.game.zoom - 2])

        text = self.font.render("Score: " + str(self.game.score), True, BLACK)

        self.screen.blit(text, [10, 10])


##### GAME CONTROL #####
game = TetrisGame()
# threading.Thread(target=game.run_game).start()
genetics = Genetics(game)
best_state = genetics.genetics()

# runs astar
# game.run_astar_or_greedy(True)
#
# # runs greedy
# game.run_astar_or_greedy(False)
