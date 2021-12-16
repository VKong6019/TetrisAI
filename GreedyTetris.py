"""
Implements a Greedy BFS approach to playing Tetris with a heuristic that favors less "holes".
"""
import util


def bfs(problem):
    # use queue for that FIFO
    frontier = util.Queue()
    # keep track of the solution or pathing as we visit each state
    # this removes/collapse the use of another dictionary to backtrack that i originally used
    frontier.push((problem.figure, [], float('inf')))
    explored = set()

    while True:
        if frontier.isEmpty():
            return ["default"]
        node = frontier.pop()
        if node[2] < problem.best_score:
            problem.best_score = node[2]
            return node[1]
        explored.add(node[0])
        successors = problem.get_successors(node[0], node[1])
        for successor in successors:
            (newState, action, new_score) = successor
            if newState not in explored and newState not in [node[0] for node in frontier.list]:
                frontier.push((newState, node[1] + [action], new_score))