from typing import List, Dict, Tuple
import logging
from .picklist import PicklistRepository
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import *

logger = logging.getLogger(__name__)

class PickSequenceService:
    """Service for handling pick sequence updates"""
    
    def __init__(self):
        self.picklist_repo = PicklistRepository()
        self.route_optimizer = RouteOptimizer()
        
    def update_pick_sequences(
        self,
        final_solution: List[int],
        picklistids: List[str],
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]]
    ) -> None:
        """
        Update pick sequences based on optimized routes
        
        Args:
            final_solution: List of picker assignments
            picklistids: List of picktask IDs
            orders_assign: List of order locations
            picktasks: List of picktask IDs
            stage_result: Staging locations
        """
        try:
            # Get optimized routes
            _, routes, assignments = self.route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS,
                final_solution,
                orders_assign,
                picktasks,
                stage_result
            )
            
            # Create mapping of locations to picklist IDs
            location_to_picklist = {}
            for idx, picklist_id in enumerate(picklistids):
                for loc in orders_assign[idx]:
                    location_to_picklist[loc] = picklist_id
            
            updates = []
            
            # Process each route
            for route in routes:
                if not route.locations:
                    continue
                    
                batch_id = f"BATCH_{route.picker_id}"
                sequence_items = []
                
                # Get picklist IDs in route order
                for loc in route.locations:
                    if loc in location_to_picklist:
                        picklist_id = location_to_picklist[loc]
                        if (picklist_id, loc) not in sequence_items:
                            sequence_items.append((picklist_id, loc))
                
                # Create sequence updates
                for seq, (picklist_id, _) in enumerate(sequence_items, 1):
                    query = """
                    SET search_path TO nifiapp;
                    UPDATE picklist 
                    SET picksequence = %s 
                    WHERE id = %s;
                    """
                    updates.append((query, (seq, picklist_id)))
                    logger.debug(f"Prepared sequence update: Batch {batch_id}, Sequence {seq} for picklist {picklist_id}")
            
            # Execute all updates in a single transaction
            self.picklist_repo.baserepository.execute_transaction(updates)
            logger.info(f"Successfully updated pick sequences for {len(final_solution)} items")
              
        except Exception as e:
            logger.error(f"Error updating pick sequences: {e}")