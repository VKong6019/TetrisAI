from collections import defaultdict

import pygame
import random
import copy

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


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y, block_type, color, rotation):
        self.x = x
        self.y = y
        if block_type is not None:
            self.type = block_type
            self.color = color
            self.rotation = rotation
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    level = 2
    score = 0
    state = "start"
    field = []
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    figure = None
    best_score = float('inf')
    optimal_move = None
    optimal_rotation = None

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0, None, None, None)
        self.best_move()

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def intersects_with_figure(self, figure, dx, dy):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    if i + dy + figure.y > self.height - 1 or \
                            j + dx + figure.x > self.width - 1 or \
                            j + dx + figure.x < 0 or \
                            self.field[i + dy + figure.y][j + dx + figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines * 100

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    # go all the way to the right, then all the way down, then all the way to the left, and then down
    def go_default(self):
        while not self.intersects():
            self.figure.x += 1
        self.figure.x -= 1
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        while not self.intersects():
            self.figure.x -= 1
        self.figure.x += 1
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def calc_heuristic_height(self, field, figure):
        for i1 in range(4):
            for j2 in range(4):
                if i1 * 4 + j2 in figure.image():
                    field[i1 + figure.y][j2 + figure.x] = figure.color

        score = 0
        for r in range(self.height):
            rule1 = 0
            rule2 = 0
            rule3 = 0
            for c in range(self.width):
                if field[r][c] == 0:
                    if r < self.height - 1 and c < self.width - 1:
                        if field[r][c + 1] != 0 or (r > 0 and field[r + 1][c + 1] != 0):
                            rule1 += 1
                    if field[r - 1][c] == 0:
                        rule2 += 1
                    if 0 < r < self.height - 1 and 0 < c < self.width - 1:
                        if field[r][c - 1] != 0 or (r > 0 and field[r - 1][c - 1] != 0):
                            rule3 += 1

            score += rule1 * (r ** 2)
            score += rule2 * (r ** 3)
            score += rule3 * (r ** 2)

        return score

    def get_successors(self, curr_figure, actions):
        successors = []

        if (len(actions) != 0 and actions[len(actions) - 1] == "space") \
                or self.intersects_with_figure(curr_figure, 0, 0):
            return successors

        # limit actions so they don't repeat
        if len(actions) == 3:
            copied_figure = Figure(curr_figure.x, curr_figure.y, curr_figure.type, curr_figure.color,
                                   curr_figure.rotation)
            successors.append(
                (curr_figure, "space", self.calc_heuristic_height(copy.deepcopy(self.field), copied_figure)))
            return successors

        copied_figure = Figure(curr_figure.x, curr_figure.y, curr_figure.type, curr_figure.color,
                               curr_figure.rotation)
        copied_figure.rotate()
        if not self.intersects_with_figure(copied_figure, 0, 0):
            successors.append(
                (copied_figure, "rotate", self.calc_heuristic_height(copy.deepcopy(self.field), copied_figure)))

        if not self.intersects_with_figure(curr_figure, 1, 0) and curr_figure.x + 1 < 7:
            copied_figure = Figure(curr_figure.x + 1, curr_figure.y, curr_figure.type, curr_figure.color,
                                   curr_figure.rotation)
            successors.append(
                (copied_figure, "right", self.calc_heuristic_height(copy.deepcopy(self.field), copied_figure)))

        if not self.intersects_with_figure(curr_figure, -1, 0):
            copied_figure = Figure(curr_figure.x - 1, curr_figure.y, curr_figure.type, curr_figure.color,
                                   curr_figure.rotation)
            successors.append(
                (copied_figure, "left", self.calc_heuristic_height(copy.deepcopy(self.field), copied_figure)))

        if not self.intersects_with_figure(curr_figure, 0, 1) and curr_figure.y + 1 < 17:
            copied_figure = Figure(curr_figure.x, curr_figure.y + 1, curr_figure.type, curr_figure.color,
                                   curr_figure.rotation)
            successors.append(
                (copied_figure, "down", self.calc_heuristic_height(copy.deepcopy(self.field), copied_figure)))

        return successors

    def get_a_star_successors(self, state):
        successors = []

        actions = ["down", "rotate", "left", "right"]
        for a in actions:
            cost = 1
            copied_figure = Figure(state[0], state[1], self.figure.type, self.figure.color,
                                   state[2])
            newState = None
            if a == "right" and state[0] < 6:
                newState = (state[0] + 1, state[1], state[2])
            elif a == "left" and state[0] > -4:
                newState = (state[0] - 1, state[1], state[2])
            elif a == "down" and state[1] < 16:
                newState = (state[0], state[1] + 1, state[2])
            elif a == "rotate":
                copied_figure.rotate()
                newState = (state[0], state[1], copied_figure.rotation)
                if copied_figure.rotation is self.optimal_rotation:
                    cost = 0
            if newState is not None:
                successors.append((newState, a, cost))

        # return a list of successors formatted as (new figure, action, cost)
        return successors

    # we want the lowest score/prioritize the lowest score
    def calculate_all_heuristics(self, figure, dx):
        field = copy.deepcopy(self.field)
        score = 0

        # drop figure all the way to bottom and calculate score
        y = 0
        while not self.intersect_at_x_y_fig(figure, dx, y):
            y += 1
        y -= 1

        for i1 in range(4):
            for j2 in range(4):
                if i1 * 4 + j2 in figure:
                    field[i1 + y][j2 + dx] = 1

        # TODO: i don't think it's counting holes correctly
        holes = 0
        for r in range(self.height):
            for c in range(self.width):
                if field[r][c] == 0 and r > 0 and field[r - 1][c] > 0:
                    holes += 1

        height = self.get_height(field)

        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
        score -= lines * 20

        return score + height + holes

    def get_height(self, field):
        for r in range(self.height):
            for c in range(self.width):
                if field[r][c] > 0:
                    return self.height - r - 1
        return 0

    def best_move(self):
        best_score = float('inf')
        work_x = None
        work_rotation = None

        for r in range(len(self.figure.figures[self.figure.type])):
            work_figure = self.figure.figures[self.figure.type][r]
            for x in range(-3, self.width):
                if not self.intersect_at_x_y_fig(work_figure, x, 0):
                    score = self.calculate_all_heuristics(work_figure, x)
                    if work_x is None or best_score > score:
                        work_rotation = r
                        work_x = x
                        best_score = score

        y = 0
        while not self.intersect_at_x_y_fig(self.figure.figures[self.figure.type][work_rotation], work_x, y):
            y += 1
        y -= 1

        self.optimal_move = (work_x, y)
        self.optimal_rotation = work_rotation

    def intersect_at_x_y_fig(self, figure, x, y):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure:
                    if i + y > self.height - 1 or \
                            j + x > self.width - 1 or \
                            j + x < 0 or \
                            self.field[i + y][j + x] > 0:
                        intersection = True
        return intersection

    def is_goal_state_a_star(self, state):
        return state[0] == self.optimal_move[0] and state[1] == self.optimal_move[
            1] and state[2] == self.optimal_rotation

    def manhattan_distance(self, xy):
        return abs(xy[0] - self.optimal_move[0]) + abs(xy[1] - self.optimal_move[1])

# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (400, 500)
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

    if game.state != "gameover":
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
            action_seq = bfs(game)

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

    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text = font.render("Score: " + str(game.score), True, BLACK)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))

    screen.blit(text, [0, 0])
    if game.state == "gameover":
        screen.blit(text_game_over, [20, 200])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
