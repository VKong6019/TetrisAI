from models.Figure import Figure
import numpy as np
import copy

line_scores = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}

rotation_map = {
    1: 'RIGHT',
    2: 'DOWN',
    3: 'LEFT',
    4: 'UP',
}


class Tetris:
    x = 100
    y = 60

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
        self.generate_board()

    # Generates new empty board
    def generate_board(self):
        self.field = []
        for _ in range(self.height):
            new_line = []
            for _ in range(self.width):
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

    ### SIMULATION ONLY ###
    # Calculates line breaks but doesn't generate new piece
    def simulate_freeze(self):
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
        self.score += lines * 100 # multiplier

    # Generates next Tetris piece
    def new_figure(self):
        self.figure = Figure(3, 0, None, None, None)
        # NOTE: Enable this if using Greedy/A*
        # self.set_optimal_move()

    # Check if gameboard intersects with current Tetromino intersects with any existing game pieces or boundaries
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

    ### SIMULATION ONLY ###
    # Check if gameboard intersects with provided figure at a specific shift dx and dy
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


    ### SIMULATION ONLY ###
    # Check if gameboard intersects with provided figure at a specific shift dx and dy
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

    ### ALGORITHMS ###

    # Calculate heuristic height using weighted holes functiom
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

    # GREEDY: Calculate valid successors by calculating new state, action, and resulting cost
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

        # check boundaries
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

    # A-STAR: Calculate valid successors by calculating new state, action, and resulting cost
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


    # GENETIC ALGORITHM: Calculate best state given a solution's weights
    def get_best_state(self, data):
        self.new_figure() # generate new Tetromino
        moves = []
        # drop optimal moves
        best_move, best_score = self.get_best_move(data)  # best_move = (self.figure.x, self.figure.y, self.figure.rotation)

        if best_move is not None:
            # Rotate figure
            while self.figure.rotation is not best_move[2]:
                self.figure.rotate()
                moves.append('rotate')
            # Move left, right, or down according to best move
            while self.figure.x is not best_move[0]:
                if self.figure.x > best_move[0] and self.figure.x >= -3:
                    self.figure.x -= 1
                    moves.append('left')
                elif self.figure.x < best_move[0] and self.figure.x <= 7:
                    self.figure.x += 1
                    moves.append('right')
            while self.figure.y is not best_move[1]:
                self.figure.y += 1
                moves.append('down')
        else:
            # default
            while not self.intersects():
                self.figure.y += 1
            self.figure.y -= 1

        self.freeze()
        # returns Tetris object, best score, and list of actions taken for move
        return self, best_score, moves

    # Calculate best move (piece drop) for given state and weights based on optimal play
    def get_best_move(self, data):
        best_score = float('inf')
        best_move = None
        curr_figure = copy.deepcopy(self.figure)
        figures = self.figure.figures[curr_figure.type]

        # calculate best move for each rotation and column position
        for r in range(len(figures)):
            curr_figure.rotation = r
            # for every column drop piece and calculate score
            for x in range(-3, self.width - 2):
                copied_state = copy.deepcopy(self)  # simulate new states
                curr_figure.x = x

                if copied_state.intersect_at_x_y_fig(curr_figure, x, 0):
                    continue

                # descend Tetromino vertically until intersects (drop)
                y = 0
                while not copied_state.intersect_at_x_y_fig(curr_figure, x, y):
                    y += 1
                y -= 1
                curr_figure.y = y
                copied_state.figure = curr_figure
                copied_state.simulate_freeze()

                # weight score by solution's genes
                raw_score = copied_state.get_score()
                score = raw_score.dot(data)

                # keep track of best move by LOWEST score (inverse scoring function)
                if score < best_score:
                    best_move = (x, y, r)
                    best_score = score

        if self.state == "gameover":
            return None, sum(self.get_score())

        self.optimal_move = (best_move[0], best_move[1])
        self.optimal_rotation = best_move[2]
        return best_move, best_score

    # GREEDY/A*: Sets the optimal move given the rotation and position of the current Tetromino
    def set_optimal_move(self):
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

        # descend Tetromino vertically until intersects (drop)
        y = 0
        while not self.intersect_at_x_y_fig(self.figure.figures[self.figure.type][work_rotation], work_x, y):
            y += 1
        y -= 1

        self.optimal_move = (work_x, y)
        self.optimal_rotation = work_rotation

    # Returns height of all columns in array (for calculate_all_heuristics)
    def get_height(self, field):
        for r in range(self.height):
            for c in range(self.width):
                if field[r][c] > 0:
                    return self.height - r - 1
        return 0

    # Prioritize lowest score
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

    # Returns height of all columns in array
    def get_heights(self, state):
        heights = []
        for c in range(state.shape[1]):
            height = self.height - next((index for index, value in enumerate(state[:, c]) if value != 0), self.height)
            heights.append(height)
        return heights

    # Returns holes found in entire board
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

    # Calculates weighted score array based on height, holes, and lines cleared
    def get_score(self):
        state = np.asarray(self.field)
        heights = self.get_heights(state)
        avg_heights = np.sum(heights) / np.count_nonzero(heights) # get average of heights of non-zero columns
        holes = self.get_holes(heights, state)
        lines = self.lines_cleared
        max_height_diff = self.get_max_height_diff(heights)
        # if lines > 0:
        #     lines ** -5.0
        return np.array([avg_heights ** 3.0, max_height_diff ** 1.3, np.sum(holes) ** 2.0, lines * -20])

    def is_goal_state_a_star(self, state):
        return state[0] == self.optimal_move[0] and state[1] == self.optimal_move[1] and state[2] == self.optimal_rotation

    def manhattan_distance(self, xy):
        return abs(xy[0] - self.optimal_move[0]) + abs(xy[1] - self.optimal_move[1])

    def get_string_field(self):
        print(np.array(self.field))
