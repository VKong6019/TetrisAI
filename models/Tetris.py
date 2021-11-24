from models.Figure import Figure
import numpy as np
import random
import copy

line_scores = { 0:0, 1: 40, 2: 100, 3: 300, 4: 1200 }

class Tetris:
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.figure = None
        self.score = 0
        self.state = "start"
        self.best_score = float('inf')
        self.optimal_move = None
        self.optimal_rotation = None

        for _ in range(height):
            new_line = []
            for _ in range(width):
                new_line.append(0)
            self.field.append(new_line)

    # Generates new piece and calculates its optimal move
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    # Checks if any lines can be cleared
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
        self.score += line_scores[lines]

    # Generates next Tetris piece and finds its best move
    def new_figure(self):
        self.figure = Figure(3, 0, None, None, None)

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


    ### MOVEMENT ###

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

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

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
        print("DEFAULT")
        self.freeze()

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    def get_string_field(self):
        print(np.array(self.field))


        ### CALCULATIONS ###
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
                        if field[r][c + 1] != 0 or (r > 0 and field[r + 1][c + 1]):
                            rule1 += 1
                    if field[r - 1][c] == 0:
                        rule2 += 1
                    if 0 < r < self.height - 1 and 0 < c < self.width - 1:
                        if field[r][c - 1] != 0 or (r > 0 and field[r - 1][c - 1]):
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
        cost = 1

        actions = ["down", "rotate", "left", "right"]
        for a in actions:
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
            if newState is not None:
                successors.append((newState, a, cost))

        # return a list of successors formatted as (new figure, action, cost)
        return successors

    # we want the lowest score/prioritize the lowest score
    def calculate_all_heuristics(self, figure, dx):
        field = copy.deepcopy(self.field)
        score = 0

        copied_figure = Figure(figure.x + dx, figure.y, figure.type, figure.color,
                                figure.rotation)
        # drop figure all the way to bottom and calculate score
        while not self.intersects_with_figure(copied_figure, 0, 0):
            copied_figure.y += 1
        copied_figure.y -= 1

        for i1 in range(4):
            for j2 in range(4):
                if i1 * 4 + j2 in copied_figure.image():
                    field[i1 + copied_figure.y][j2 + copied_figure.x] = copied_figure.color

        holes = 0
        for r in range(self.height):
            for c in range(self.width):
                if field[r][c] == 0 and r > 0 and field[r - 1][c] == 0:
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
        score -= lines ** 20

        return score + height + holes

    def get_height(self, field):
        for c in range(self.width):
            for r in range(self.height):
                if field[r][c] == 1:
                    return self.height - r - 1
        return 0

    def best_move(self):
        best_score = float('inf')
        work_x = None
        work_rotation = None

        for r in range(len(self.figure.figures[self.figure.type])):
            for x in range(-3, self.width):
                if not self.intersects_with_figure(self.figure, x, 0) and self.figure.x + x < 7:
                    score = self.calculate_all_heuristics(self.figure, x)
                    if work_x is None or best_score > score:
                        work_rotation = r
                        work_x = x
                        best_score = score

        copied_figure = Figure(work_x, self.figure.y, self.figure.type, self.figure.color,
                                work_rotation)
        while not self.intersects_with_figure(copied_figure, 0, 0):
            copied_figure.y += 1
        copied_figure.y -= 1

        self.optimal_move = (work_x, copied_figure.y)
        self.optimal_rotation = work_rotation

    def is_goal_state_a_star(self, state):
        return state[0] == self.optimal_move[0] and state[1] == self.optimal_move[
            1] and state[2] == self.optimal_rotation

    def manhattan_distance(self, xy):
        return abs(xy[0] - self.optimal_move[0]) + abs(xy[1] - self.optimal_move[1])

    def get_string_field(self):
        print(np.array(self.field))