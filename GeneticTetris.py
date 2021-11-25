import random
import numpy as np

from models.Figure import Figure
    
NUM_GENES = 10
MUTATION_PROB = 0.1
NUM_SIMULATIONS = 4
SIMULATION_LENGTH = 10

# Represents a possible solution for current game state
class Solution():
    def __init__(self, state):
        self.game = state
        self.fitness = None
        self.genes = self.generateGenes()
        self.simulations = NUM_SIMULATIONS
        self.max_simulations = SIMULATION_LENGTH
        self.mutation_prob = MUTATION_PROB


    # generate random genetic values
    def generateGenes(self):
        return (np.random.random_sample(NUM_GENES) * 2) - 1

    # Calculate overall score rating for move
    def getFitness(self):
        scores = []
        for i in range(self.max_simulations):
            # generate random tetromino and simulate best move
            self.game.new_figure()
            bestState, bestScore = self.game.getBestMove(self.game.figure, self.genes)
            print("BEST SCORE: ", bestScore)
            # self.game.get_string_field()
            scores.append(bestScore)
        return np.average(scores)

    # Cross genes between two solutions
    def reproduceWith(solution2):
        # Compare weighted average between genetic values of chromosomes
        return

    # 
    def mutate():
        return


class Genetics():

    def __init__(self, state):
        self.problem = state # stores figure information (x, y, rotation)
        self.size = NUM_GENES
        self.solutions = [Solution(state) for i in range(self.size)] # initialize population of possible solutions
        self.generations = 0
        # self.weights =
        self.fitness = None

    def weightedBy(self, solutions):
        return

    def weightedRandomChoices(self, solutions, weights):
        return

    # returns the best individual given possible solutions and fitness weight function
    def genetics(self, solutions):
        # select most fit individuals
        while True:
            # assign each individual a fitness value according to fitness function
            new_solutions = []
            weights = self.weightedBy(solutions)

            for i in range(solutions):
                curr_solution = solutions[i]
                solution1, solution2 = self.weightedRandomChoices(solutions, weights)
                new_solution = curr_solution.reproduceWith(solution2)
                
                # mutate occasionally
                if (random.random() < 0.2):
                    new_solution = curr_solution.mutate(new_solution)
                new_solutions.append(new_solution)
            solutions = new_solutions
        return bestMove
