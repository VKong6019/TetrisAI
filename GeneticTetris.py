import random

class GeneticTetris():

    def __init__(self, genes, population):
        # initialize population of possible solutions
        self.genes = genes
        self.population = population
        self.generations = 0
        self.fitness = self.getFitness()

    def getFitness(self):
        

    def weightedBy(moves):
        return

    def weightedRandomChoices(moves, weights):
        return

    def reproduce(move1, move2):

    def mutate(move):
        return

    # returns the best individual given possible moves and fitness weight function
    def getBestMove(moves):
        # select most fit individuals
        while True:
            # assign each individual a fitness value according to fitness function
            newMoves = []
            weights = weightedBy(moves)

            for 1 in range(moves):
                move1, move2 = weightedRandomChoices(moves, weights)
                newMove = reproduce(move1, move2)
                
                # mutate occasionally
                if (random.random() < 0.2):
                    newMove = mutate(newMove)
                newMoves.append(newMove)
            moves = newMoves
        return bestMove

