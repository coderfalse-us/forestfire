import numpy as np
from ..utils.config import ALPHA, BETA, RHO, Q

class AntColony:
    def __init__(self, num_ants, alpha=ALPHA, beta=BETA, rho=RHO):
        """
        Initialize ACO algorithm parameters
        
        Args:
            num_ants: Number of ants in the colony
            alpha: Pheromone importance factor
            beta: Heuristic information importance factor  
            rho: Pheromone evaporation rate
        """
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        
    def initialize_pheromone(self, num_items, num_pickers):
        """Initialize pheromone matrix with ones"""
        return np.ones((num_items, num_pickers))
        
    def construct_solution(self, pheromone):
        """Construct a solution using ant colony rules"""
        num_items, num_pickers = pheromone.shape
        solution = []
        
        for item in range(num_items):
            # Calculate probabilities for picker selection
            probabilities = self._calculate_probabilities(
                pheromone[item], 
                item,
                num_pickers
            )
            
            # Select picker based on probabilities
            picker = np.random.choice(num_pickers, p=probabilities)
            solution.append(picker)
            
        return solution
    
    def _calculate_probabilities(self, pheromone_values, item, num_pickers):
        """Calculate probabilities for picker selection"""
        numerators = np.power(pheromone_values, self.alpha)
        denominator = np.sum(numerators)
        
        return numerators / denominator
        
    def update_pheromone(self, pheromone, solution, solution_score):
        """Update pheromone trails"""
        # Evaporation
        pheromone *= (1 - self.rho)
        
        # Deposit new pheromone
        for item, picker in enumerate(solution):
            deposit = Q / (solution_score + 1e-10)  # Avoid division by zero
            pheromone[item][picker] += deposit
            
        return pheromone
        
    def _get_heuristic_info(self, item, picker):
        """Get heuristic information (distance-based)"""
        # This could be extended to include actual distance calculations
        # between items and pickers
        return 1.0  # Placeholder for now