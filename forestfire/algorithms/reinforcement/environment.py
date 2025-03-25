# forestfire/algorithms/reinforcement/environment.py
from typing import Tuple, List, Dict
import numpy as np
import gym
from gym import spaces
from forestfire.utils.config import *
from forestfire.optimizer.services.routing import RouteOptimizer

class WarehouseEnvironment(gym.Env):
    """Custom Environment for Warehouse Picker Routing"""
    
    def __init__(
        self, 
        orders_assign: List[List[Tuple[float, float]]], 
        picker_locations: List[Tuple[float, float]],
        picker_capacities: List[int]
    ):
        super().__init__()
        
        self.orders_assign = orders_assign
        self.picker_locations = picker_locations
        self.picker_capacities = picker_capacities
        self.route_optimizer = RouteOptimizer()
        
        # Action space: Which picker to assign current item to
        self.action_space = spaces.Discrete(NUM_PICKERS)
        
        # Observation space: Current state of assignments and picker loads
        self.observation_space = spaces.Dict({
            'remaining_items': spaces.Box(
                low=0, high=1, shape=(len(orders_assign),), dtype=np.int32
            ),
            'picker_loads': spaces.Box(
                low=0, high=max(picker_capacities), 
                shape=(NUM_PICKERS,), dtype=np.int32
            ),
            'current_item': spaces.Box(
                low=0, high=len(orders_assign), shape=(1,), dtype=np.int32
            )
        })
        
        self.reset()
        
    def reset(self):
        """Reset environment to initial state"""
        self.remaining_items = np.ones(len(self.orders_assign))
        self.picker_loads = np.zeros(NUM_PICKERS)
        self.current_item = 0
        self.assignment = [-1] * len(self.orders_assign)
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[Dict, float, bool, Dict]:
        """Execute action and return new state"""
        # Check if action is valid
        if self.picker_loads[action] >= self.picker_capacities[action]:
            return self._get_observation(), -1000, True, {}
            
        # Assign current item to chosen picker
        self.assignment[self.current_item] = action
        self.picker_loads[action] += 1
        self.remaining_items[self.current_item] = 0
        
        # Calculate immediate reward
        reward = self._calculate_reward(action)
        
        # Move to next item
        self.current_item += 1
        done = (self.current_item >= len(self.orders_assign))
        
        if done:
            # Add final route optimization reward
            total_cost, _, _ = self.route_optimizer.calculate_shortest_route(
                self.picker_locations,
                self.assignment,
                self.orders_assign,
                [],  # picktasks not needed for reward calculation
                {}   # stage_result not needed for reward calculation
            )
            reward -= total_cost
            
        return self._get_observation(), reward, done, {}
    
    def _get_observation(self) -> Dict:
        """Get current state observation"""
        return {
            'remaining_items': self.remaining_items,
            'picker_loads': self.picker_loads,
            'current_item': np.array([self.current_item])
        }
        
    def _calculate_reward(self, action: int) -> float:
        """Calculate immediate reward for action"""
        # Base reward for valid assignment
        reward = 0
        
        # Penalty for uneven load distribution
        std_dev = np.std(self.picker_loads)
        reward -= std_dev * 10
        
        # Distance-based reward
        current_item_locs = self.orders_assign[self.current_item]
        picker_loc = self.picker_locations[action]
        min_distance = float('inf')
        
        for loc in current_item_locs:
            distance = np.sqrt((loc[0] - picker_loc[0])**2 + 
                             (loc[1] - picker_loc[1])**2)
            min_distance = min(min_distance, distance)
        
        reward -= min_distance
        
        return reward