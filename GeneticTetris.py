import random

class GeneticTetris():

    def __init__(self):
        # initialize population of possible solutions
        return None

    def weightedBy(moves, fitness):
        return

    def weightedRandomChoices(moves, weights):
        return

    def mutate(move):
        return

    # returns the best individual given possible moves and fitness weight function
    def getBestMove(moves, fitness):
        # select most fit individuals
        while True:
            # assign each individual a fitness value according to fitness function
            newMoves = []
            weights = weightedBy(moves, fitness)

            for 1 in range(moves):
                move1, move2 = weightedRandomChoices(moves, weights)
                newMove = reproduce(move1, move2)
                
                # mutate occasionally
                if (random.random() < 0.2):
                    newMove = mutate(newMove)
                newMoves.append(newMove)
            moves = newMoves
        return bestMove

