import random
import numpy as np

import time
from models.Tetris import Tetris
from models.Figure import Figure
    
NUM_GENERATIONS = 10
NUM_GENES = 4
POPULATION_SIZE = 5
MUTATION_PROB = 0.1
NUM_SIMULATIONS = 4
SIMULATION_LENGTH = 20

# Represents a possible solution for current game state
class Solution():
    def __init__(self, state):
        self.state = state
        self.fitness = None
        self.weights = self.generateWeights()
        print(self.weights)
        self.simulations = NUM_SIMULATIONS
        self.max_simulations = SIMULATION_LENGTH
        self.mutation_prob = MUTATION_PROB
        self.generations = NUM_GENERATIONS

    # generate random genetic values that represents weights
    def generateWeights(self):
        print("Generate genes: ", (np.random.random_sample(NUM_GENES) * 2))
        return (np.random.random_sample(NUM_GENES) * 2)

    # gets solution's fitness if exists, if not, then calculates fitness
    def getFitness(self):
        if self.fitness:
            return self.fitness
        return self.calculateFitness()

    # Calculate overall score rating for move
    def calculateFitness(self):
        # start game for this solution
        self.state.reset_game()
        scores = []
        for i in range(self.max_simulations):
            # print("SIMULATION #", i)
            if self.state.game.state == "gameover":
                # time.sleep(2)
                return np.average(scores)
            # generate random tetromino and simulate best move
            print("HELLO 2")
            self.state.game.new_figure()
            # print("GENES: ", self.weights)
            best_state, best_score, _ = self.state.game.get_best_state(self.weights)
            self.state.game = best_state
            scores.append(best_score)
            self.state.game.get_best_move(self.weights)

        print("FITNESS: ", np.average(scores))
        return np.average(scores)

    # Cross genes between two solutions
    def reproduceWith(self, solution2):
        # Compare weighted average between genetic values of solutions
        weighted_avg = self.getFitness() + solution2.getFitness()
        solution2_weight = solution2.weights.dot(solution2.getFitness())
        # Combine genes
        combined_solution = (self.weights * self.getFitness()) + (solution2_weight / weighted_avg)
        return combined_solution

    # Mutate weights
    def mutate(self, solution2):
        print("ASJDKAJSKDJKAS")
        print(self.weights)
        mutation_amt = np.random.random_sample(self.weights)
        if (mutation_amt < self.mutation_prob):
            solution2_weight = solution2.weights.dot(mutation_amt)
            genes = (self.weights * (1 - mutation_amt)) + solution2_weight
            self.weights = genes
        return self


class Genetics():

    def __init__(self, game):
        self.state = game
        self.size = POPULATION_SIZE
        self.solutions = [Solution(self.state) for i in range(self.size)] # initialize population of possible solutions
        self.generations = NUM_GENERATIONS
        self.fitness = None

    def weightedBy(self):
        print(sorted(self.solutions, key=lambda gene: gene.getFitness()))
        return sorted(self.solutions, key=lambda gene: gene.getFitness())

    # TODO
    def weightedRandomChoices(self, solutions, weights):
        return

    def getBestIndividual(self, solutions):
        print(sorted(solutions, key=lambda gene: gene.calculateFitness()))
        return sorted(solutions, key=lambda gene: gene.calculateFitness())


    # TODO:
    # - generate list of moves to return(?)
    # - each solution should represent genes of scoring weights
    # - return solution with best weighted outcome


    # returns the best individual given possible solutions and fitness weight function
    def genetics(self):
        # assign each individual a fitness value according to fitness function
        new_solutions = []
        weights = self.weightedBy() # list of corresponding fitness values for each individual

        for i in range(self.generations):
            print("GENERATION # ", i)
            # time.sleep(2)
            # print([solution.calculateFitness() for solution in weights])
            # Get top half fittest solutions
            top_half = len(self.solutions) // 2
            # select most fit individuals
            fittest_solutions = weights[top_half:]
            for g in fittest_solutions:
                print("FIT: ", g.getFitness())
                print("WEIGHTS: ", g.weights)
            # Crossbreed surviving solutions
            print("TOP: ", top_half)
            for s in range(0, top_half, 2):
                curr_solution = fittest_solutions[s]
                # solution1, solution2 = self.weightedRandomChoices(self.solutions, weights) # TODO
                print(curr_solution)
                if s < len(fittest_solutions):
                    solution2 = fittest_solutions[s+1]
                    new_solution = curr_solution.reproduceWith(solution2)
                
                    # mutate occasionally
                    if (random.random() < 0.2):
                        new_solution = curr_solution.mutate(new_solution)
                    print("NEW SOLUTION: ", new_solution)
                    new_solutions.append(new_solution)
        print("SOLUTIONS: ", new_solutions)
        return self.getBestIndividual(new_solutions)
