import random
import numpy as np
import time
import copy
from models.Tetris import Tetris
from models.Figure import Figure
    
NUM_GENERATIONS = 3
NUM_GENES = 4
POPULATION_SIZE = 10
MUTATION_PROB = 0.1
NUM_SIMULATIONS = 4
SIMULATION_LENGTH = 100

# Solution represents a Tetris game state and holds the current playing board, a fitness score, weights, which represent the 'genes' of the solution that is multiplied by the weighted heuristic, number of simulations, mutation probability, and number of generations.
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
        if self.fitness:
            return self.fitness

        # start game for this solution
        self.state.reset_game()
        return self.calculateFitness()

    # Calculate overall score rating for move based on Tetris scoring
    def calculateFitness(self):
        scores = []
        for _ in range(self.max_simulations):
            if self.state.game.state == "gameover":
                print("FITNESS: ", np.average(scores))
                print("LINES CLEARED: ", self.state.game.lines_cleared)
                return np.average(scores)
            # generate random tetromino and simulate best move
            best_state, best_score, moves = self.state.game.get_best_state(self.weights)
            self.state.action_seq = moves
            self.state.game = best_state
            scores.append(best_score)
            self.state.game.get_best_move(self.weights)
            self.state.game.get_string_field()
        # print("FITNESS: ", np.average(scores))
        # print("LINES CLEARED: ", self.state.game.lines_cleared)
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
        self.calculateFitness()
        return self

    # Mutate weights
    def mutate(self, solution2):
        mutation_amt = np.random.random_sample()
        if (mutation_amt < self.mutation_prob):
            solution2_weight = solution2.weights.dot(mutation_amt)
            genes = (self.weights * (1 - mutation_amt)) + solution2_weight
            self.weights = genes
        return self


# Provides objects and evolutionary methods relevant to genetics algorithm in order to simulate genetics algorithm on a given population of Tetris games over a number of generations. The outcome is 
class Genetics():

    def __init__(self, game):
        self.state = game
        self.size = POPULATION_SIZE
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
        return solutions

    # prints results from each generation
    def printGenerations(self, solutions):
        print('#######################')
        print(solutions)
        for s in solutions:
            print('Fitness: ', s.getFitness())
            print('Weights: ', s.weights)
            # print('Score: ', np.mean(s.getFitness()))

        print('#######################')


    # returns the best individual given possible solutions and fitness weight function
    def genetics(self):
        # assign each individual a fitness value according to fitness function
        new_solutions = []

        # each solution represents solution's genes of scoring weights
        for i in range(self.generations):
            time.sleep(5)
            print("GENERATION # ", i)
            weights = self.weightedBy() # List of corresponding fitness values for each individual
            top_half = len(self.solutions) // 2 # Get top half fittest solutions
            fittest_solutions = weights[top_half:] # Select most fit individuals

            # Crossbreed surviving solutions
            for s in range(0, top_half - 1, 2):
                curr_solution = fittest_solutions[s]
                solution2 = fittest_solutions[s+1]
                new_solution = curr_solution.reproduceWith(solution2)
            
                # mutate occasionally
                if (random.random() < 0.2):
                    new_solution = curr_solution.mutate(new_solution)
                
                new_solution.state.game.get_string_field()
                new_solutions.append(new_solution)
                print("NEW FITNESS")
                print(new_solution.calculateFitness())

        self.printGenerations(new_solutions)
        # return self.getBestIndividual(new_solutions)
