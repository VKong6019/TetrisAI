from models.Figure import Figure
import numpy as np
import random
import time
import copy

line_scores = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}

rotation_map = {
    1: 'RIGHT',
    2: 'DOWN',
    3: 'LEFT',
    4: 'UP',
}

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
        self.moves = 0
        self.lines_cleared = 0
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

    # Calculates line breaks but doesn't generate new piece
    # Used for simulations
    def simulate_freeze(self):
        # print("FREEZE: ", self.figure.image())
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
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
                self.lines_cleared += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += line_scores[lines]

    # Generates next Tetris piece
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
                    print("X: ", figure.x, "Y: ", figure.y)
                    if i + dy + figure.y > self.height - 1 or \
                            j + dx + figure.x > self.width - 1 or \
                            j + dx + figure.x < 0 or \
                            self.field[i + dy + figure.y][j + dx + figure.x] > 0:
                        intersection = True
        return intersection

    # TODO: Misses edge case
    def intersect_at_x_y_fig(self, figure, x, y):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    if i + y > self.height - 1 or \
                            j + x > self.width - 1 or \
                            j + x < 0 or \
                            self.field[i + y][j + x] > 0:
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
        self.freeze()

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

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
            copied_figure = Figure(state[0], state[1], self.figure.type, self.figure.color, state[2])
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

    #########################################
    # GENETIC ALGORITHM:
    # Calculate best state given a solution's weights
    def get_best_state(self, data):
        self.new_figure()
        moves = []
        # drop optimal moves
        # self.get_string_field()
        # time.sleep(0.5)
        best_move, best_score = self.get_best_move(data)  # best_move = (self.figure.x, self.figure.y, self.figure.rotation)
        # print("BEST SCORE: ", best_score)
        if best_move is not None:
            # Rotate figure
            while self.figure.rotation is not best_move[2]:
                self.figure.rotate()
                moves.append('rotate')
            # Move left or right
            while self.figure.x is not best_move[0]:
                # print("BEST MOVE: ", best_move[0])
                # print("FIGURE X: ", self.figure.x)
                if self.figure.x > best_move[0] and self.figure.x >= -3:
                    # TODO: Bug when self.figure.x = -1 and best_move[0] = -2
                    self.figure.x -= 1
                    # print("SHIFT LEFT: ", self.figure.x)
                    # print(self.figure.x)
                    # print(best_move[0])
                    moves.append('left')
                elif self.figure.x < best_move[0] and self.figure.x <= 7:
                    self.figure.x += 1
                    # print("SHIFT RIGHT: ", self.figure.x)
                    # print(self.figure.x)
                    # print(best_move[0])
                    moves.append('right')
                # self.get_string_field()
                # time.sleep(0.5)
            while self.figure.y is not best_move[1]:
                self.figure.y += 1
                moves.append('down')
        else:
            # default
            while not self.intersects():
                self.figure.y += 1
            self.figure.y -= 1

        self.freeze()
        # TODO: CHECK
        # print("FINAL STATE: ")
        # self.get_string_field()
        # time.sleep(5)
        return self, best_score, moves


    # Calculate best move (piece drop) for given state and weights based on optimal play
    def get_best_move(self, data):
        best_score = float('inf')
        best_move = None
        # calculate best move for each rotation
        curr_figure = copy.deepcopy(self.figure)
        figures = self.figure.figures[curr_figure.type]
        for r in range(len(figures)):
            curr_figure.rotation = r
            # for every column drop piece and calculate score
            for x in range(-3, self.width - 2):
                copied_state = copy.deepcopy(self) # simulate new states
                curr_figure.x = x
                if copied_state.intersect_at_x_y_fig(curr_figure, x, 0):
                    # print("OUTTA BOUND: ", x)
                    continue
                y = 0
                while not copied_state.intersect_at_x_y_fig(curr_figure, x, y):
                    y += 1
                y -= 1
                # print("INTERSECTED Y: ", curr_figure.y)
                curr_figure.y = y
                copied_state.figure = curr_figure
                copied_state.simulate_freeze()
                copied_state.get_string_field()
                # weight score by solution's genes
                raw_score = copied_state.get_score()
                score = raw_score.dot(data)
                print("SCORE ", score)
                time.sleep(0.5)

                # keep track of best move by LOWEST score
                if score < best_score:
                    best_move = (x, y, r)
                    best_score = score
        
        
        if self.state == "gameover":
            return None, sum(self.get_score())
        
        # self.optimal_move = (best_move[0], best_move[1])
        # self.optimal_rotation = best_move[2]
        return best_move, best_score

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

    # TODO: Fix??
    def get_height(self, field):
        for c in range(self.width):
            for r in range(self.height):
                if field[r][c] == 1:
                    return self.height - r - 1
        return 0

    # Returns height of all columns in array
    def get_heights(self, state):
        heights = []
        for c in range(state.shape[1]):
            height = self.height - next((index for index, value in enumerate(state[:, c]) if value != 0), self.height)
            heights.append(height)
        return heights

    def get_holes(self, heights, state):
        holes = []
        for c in range(state.shape[1]):
            start = -heights[c]  # check if there are any holes
            if start == 0:
                holes.append(0)
            else:
                holes.append(np.count_nonzero(state[int(start):, c] == 0))
        return holes

    # Returns max height difference of columns in array
    def get_max_height_diff(self, state):
        return np.max(state) - np.min(state)

    # Provides weighted score array
    def get_score(self):
        state = np.asarray(self.field)
        heights = self.get_heights(state)
         # get average of heights of non-zero columns
        avg_heights = np.sum(heights) / np.count_nonzero(heights)
        holes = self.get_holes(heights, state)
        lines = self.lines_cleared
        if lines > 0:
            lines ** -5.0
        max_height_diff = self.get_max_height_diff(state)
        print(np.array([avg_heights ** 2.0, max_height_diff ** 1.3, np.sum(holes), lines]))
        return np.array([avg_heights ** 2.0, max_height_diff ** 1.3, np.sum(holes), lines])

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
