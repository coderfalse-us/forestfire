from typing import List, Tuple, Optional
import random
import numpy as np
from ..optimizer.fitness import FitnessCalculator

class GeneticAlgorithm:
    def __init__(
        self,
        pop_size: int,
        crossover_prob: float,
        mutation_prob: float,
        tournament_size: int
    ):
        self.pop_size = pop_size
        self.pc = crossover_prob
        self.pm = mutation_prob
        self.tournament_size = tournament_size

    def initialize_population(
        self, 
        num_items: int, 
        num_pickers: int
    ) -> List[List[int]]:
        """Initialize random population with capacity constraints"""
        population = []
        
        for _ in range(self.pop_size):
            solution = []
            assigned_counts = [0] * num_pickers
            
            for _ in range(num_items):
                valid_pickers = [
                    i for i, count in enumerate(assigned_counts) 
                    if count < self.picker_capacities[i]
                ]
                picker = random.choice(valid_pickers)
                assigned_counts[picker] += 1
                solution.append(picker)
                
            population.append(solution)
            
        return population

    def crossover(self, population: List[List[int]]) -> List[List[int]]:
        """Perform crossover operations"""
        offspring = []
        
        for _ in range(self.pop_size // 2):
            if random.random() < self.pc:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                # Choose crossover type randomly
                if random.random() < 0.5:
                    child1, child2 = self._single_point_crossover(parent1, parent2)
                else:
                    child1, child2 = self._uniform_crossover(parent1, parent2)
                    
                offspring.extend([child1, child2])
                
        return offspring

    def mutate(self, population: List[List[int]]) -> List[List[int]]:
        """Perform mutation operations"""
        mutants = []
        
        for solution in population:
            if random.random() < self.pm:
                mutant = solution.copy()
                
                # Swap mutation with capacity constraints
                attempts = 10
                while attempts > 0:
                    i = random.randint(0, len(mutant) - 1)
                    new_picker = random.randint(0, len(self.picker_capacities) - 1)
                    
                    old_picker = mutant[i]
                    mutant[i] = new_picker
                    
                    # Check capacity constraints
                    counts = [mutant.count(p) for p in range(len(self.picker_capacities))]
                    if all(counts[p] <= self.picker_capacities[p] for p in range(len(counts))):
                        break
                        
                    mutant[i] = old_picker
                    attempts -= 1
                    
                mutants.append(mutant)
                
        return mutants

    def select_next_generation(
        self, 
        combined_pop: List[List[int]], 
        fitness: FitnessCalculator
    ) -> List[List[int]]:
        """Select next generation using elitism"""
        sorted_pop = sorted(combined_pop, key=lambda x: fitness.evaluate(x))
        return sorted_pop[:self.pop_size]

    def _tournament_selection(self, population: List[List[int]]) -> List[int]:
        """Select individual using tournament selection"""
        tournament = random.sample(population, self.tournament_size)
        return min(tournament, key=lambda x: self.fitness.evaluate(x))

    def _single_point_crossover(
        self, 
        parent1: List[int], 
        parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Perform single point crossover"""
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def _uniform_crossover(
        self, 
        parent1: List[int], 
        parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Perform uniform crossover"""
        child1, child2 = [], []
        
        for i in range(len(parent1)):
            if random.random() < 0.5:
                child1.append(parent1[i])
                child2.append(parent2[i])
            else:
                child1.append(parent2[i])
                child2.append(parent1[i])
                
        return child1, child2