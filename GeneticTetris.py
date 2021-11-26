import random
import numpy as np

from models.Figure import Figure
    
NUM_GENERATIONS = 5
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
        print("Generate genes: ", (np.random.random_sample(NUM_GENES) * 2) - 1)

        return (np.random.random_sample(NUM_GENES) * 2) - 1

    # Calculate overall score rating for move
    def getFitness(self):
        scores = []
        for i in range(self.max_simulations):
            # generate random tetromino and simulate best move
            self.game.new_figure()
            print("GENES: ", self.genes)
            best_state, best_score = self.game.getBestState(self.genes)
            self = best_state
            print("BEST STATE: ", best_state.get_string_field())
            scores.append(best_score)
        return np.average(scores)

    # Cross genes between two solutions
    def reproduceWith(self, solution2):
        # Compare weighted average between genetic values of solutions
        weighted_avg = self.getFitness() + solution2.getFitness()
        # Combine genes
        combined_solution = ((self.genes * self.getFitness()) + (solution2.genes * solution2.getFitness())) / weighted_avg
        return combined_solution

    # Mutate weights
    def mutate(self, solution2):
        mutation_amt = np.random.random_sample(self.genes)
        if (mutation_amt < self.mutation_prob):
            genes = (self.genes * (1 - mutation_amt)) + (solution2.genes * mutation_amt)
            self.genes = genes
        return self


class Genetics():

    def __init__(self, state):
        self.problem = state # stores figure information (x, y, rotation)
        self.size = NUM_GENES
        self.solutions = [Solution(state) for i in range(self.size)] # initialize population of possible solutions
        self.generations = NUM_GENERATIONS
        self.fitness = None

    def weightedBy(self):
        return sorted(self.solutions, key=lambda gene: gene.getFitness())

    def weightedRandomChoices(self, solutions, weights):
        return

    def getBestIndividual(self, solutions):
        return sorted(solutions, key=lambda gene: gene.getFitness())[-1]


    # TODO:
    # - generate list of moves to return
    # - each solution should represent 


    # returns the best individual given possible solutions and fitness weight function
    def genetics(self):

        # assign each individual a fitness value according to fitness function
        new_solutions = []
        weights = self.weightedBy() # list of corresponding fitness values for each individual

        for i in range(self.generations):
            print("GENERATION # ", i)
            print([solution.getFitness() for solution in weights])
            # Get top half fittest solutions
            top_half = len(self.solutions) // 2
            # select most fit individuals
            fittest_solutions = weights[top_half:]

            # Crossbreed surviving solutions
            for s in range(top_half, 2):
                curr_solution = self.fittest_solutions[s]
                solution1, solution2 = self.weightedRandomChoices(self.solutions, weights) # TODO

                new_solution = curr_solution.reproduceWith(solution2)
                
                # mutate occasionally
                if (random.random() < 0.2):
                    new_solution = curr_solution.mutate(new_solution)
                print("NEW SOLUTION: ", new_solution)
                new_solutions.append(new_solution)
        print(new_solutions)
        return self.getBestIndividual(new_solutions)
