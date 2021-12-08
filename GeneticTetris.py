import random
import numpy as np
import time
import copy
from models.Tetris import Tetris
from models.Figure import Figure
    
NUM_GENERATIONS = 10
NUM_GENES = 4
POPULATION_SIZE = 10
MUTATION_PROB = 0.1
NUM_SIMULATIONS = 4
SIMULATION_LENGTH = 100

# Represents a possible solution for current game state
class Solution():
    def __init__(self, state):
        self.state = state
        self.fitness = None
        self.weights = self.generateWeights()
        self.simulations = NUM_SIMULATIONS
        self.max_simulations = SIMULATION_LENGTH
        self.mutation_prob = MUTATION_PROB
        self.generations = NUM_GENERATIONS

    # generate random genetic values that represents weights
    def generateWeights(self):
        print("Generate genes: ", (np.random.random_sample(NUM_GENES) * 2))
        return (np.random.random_sample(NUM_GENES) * 2)

    # gets solution's fitness if exists, if not, then calculates fitness, which represents the solution's score
    def getFitness(self):
        time.sleep(2)
        if self.fitness:
            return self.fitness

        # start game for this solution
        self.state.reset_game()
        return self.calculateFitness()

    # Calculate overall score rating for move
    def calculateFitness(self):
        scores = []
        for _ in range(self.max_simulations):
            # print("SIMULATION #", i)
            if self.state.game.state == "gameover":
                # time.sleep(2)
                return np.average(scores)
            # generate random tetromino and simulate best move
            # print("GENES: ", self.weights)
            best_state, best_score, moves = self.state.game.get_best_state(self.weights)
            # print("MOVES: ", moves)
            # time.sleep(2)
            self.state.action_seq = moves
            self.state.game = best_state
            scores.append(best_score)
            self.state.game.get_best_move(self.weights)
            self.state.game.get_string_field()
        print("FITNESS: ", np.average(scores))
        print("LINES CLEARED: ", self.state.game.lines_cleared)
        self.fitness = np.average(scores)
        return self.fitness

    # Cross genes between two solutions
    def reproduceWith(self, solution2):
        # Compare weighted average between genetic values of solutions
        weighted_avg = self.getFitness() + solution2.getFitness()
        solution2_weight = solution2.weights.dot(solution2.getFitness())
        # Combine gene weights
        for i, weight in enumerate(self.weights):
            self.weights[i] = ((weight * self.getFitness()) + (solution2_weight[i] * solution2.getFitness())) / weighted_avg
        print(self.weights)
        time.sleep(2)
        return self

    # Mutate weights
    def mutate(self, solution2):
        # print(self.weights)
        mutation_amt = np.random.random_sample()
        if (mutation_amt < self.mutation_prob):
            solution2_weight = solution2.weights.dot(mutation_amt)
            genes = (self.weights * (1 - mutation_amt)) + solution2_weight
            self.weights = genes
        return self


# Represents the game state and objects relevant to genetics algorithm
class Genetics():

    def __init__(self, game):
        self.state = game
        self.size = POPULATION_SIZE
        # TODO: FIX
        # self.state.run_game()
        self.solutions = [Solution(self.state) for i in range(self.size)] # initialize population of possible solutions
        self.generations = NUM_GENERATIONS
        self.fitness = None

    def weightedBy(self):
        return sorted(self.solutions, key=lambda gene: gene.calculateFitness())

    def getBestIndividual(self, solutions):
        print(sorted(solutions, key=lambda gene: sum(gene.getFitness())))
        return sorted(solutions, key=lambda gene: sum(gene.getFitness()))

    # Compiles all solution results
    def getAllSolutions(self):
        solutions = []
        for s in self.solutions:
            solutions.append((s.getFitness(), s.weights))
            print("FIT: ", s.getFitness())
            print("WEIGHTS: ", s.weights)
        print(solutions)
        return solutions

    # prints results from each generation
    def printGenerations(self, solutions):
        print('#######################')
        print(solutions)
        for s in solutions:
            print('Fitness: ', s.getFitness())
            print('Score: ', np.mean(s.getFitness()))

        print('#######################')


    # TODO:
    # - generate list of moves to return(?)

    # returns the best individual given possible solutions and fitness weight function
    def genetics(self):
        # assign each individual a fitness value according to fitness function
        new_solutions = []
        # each solution represents solution's genes of scoring weights

        for i in range(self.generations):
            print("GENERATION # ", i)
            # list of corresponding fitness values for each individual
            weights = self.weightedBy() 
            print("TOP SOLUTION: ", weights[-1].fitness, weights[-1].weights)
            time.sleep(2)
            # Get top half fittest solutions
            top_half = len(self.solutions) // 2
            # select most fit individuals
            fittest_solutions = weights[top_half:]

            # Crossbreed surviving solutions
            for s in range(0, top_half - 1, 2):
                curr_solution = fittest_solutions[s]
                solution2 = fittest_solutions[s+1]
                new_solution = curr_solution.reproduceWith(solution2)
            
                # mutate occasionally
                if (random.random() < 0.2):
                    new_solution = curr_solution.mutate(new_solution)
                new_solutions.append(new_solution)
        # self.printGenerations(new_solutions)
        return self.getBestIndividual(new_solutions)
