import util


def aStarSearch(problem):
    """Search the node that has the lowest combined cost and heuristic first."""
    # use priority queue to prioritize the cumulative cost + heuristics given a function
    frontier = util.PriorityQueue()
    # keep track of the solution or pathing as we visit each state
    frontier.push(((problem.figure.x, problem.figure.y, problem.figure.rotation), [], 0), problem.manhattan_distance((problem.figure.x, problem.figure.y)))
    explored = set()

    while True:
        if frontier.isEmpty():
            return ["default"]
        node = frontier.pop()
        if problem.is_goal_state_a_star(node[0]):
            return node[1] + ["down"]
        explored.add(node[0])
        successors = problem.get_a_star_successors(node[0])
        for successor in successors:
            (newState, action, cost) = successor
            nodesInFrontier = [item[2][0] for item in frontier.heap]
            newCost = node[2] + cost
            newPriority = newCost + problem.manhattan_distance(newState)
            # don't add newPriority in node since we don't keep track of all heuristics on path cost
            newNode = (newState, node[1] + [action], newCost)
            if newState not in explored and newState not in nodesInFrontier:
                frontier.push(newNode, newPriority)
            elif newState in nodesInFrontier \
                    and next(item[2][2] for item in frontier.heap if item[2][0] == newState) > newPriority:
                # this case is specific for A* approach by updating the new path cost + heuristic of current node
                frontier.update(newNode, newPriority)