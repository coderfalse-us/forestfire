"""
Service for handling batch pick sequence operations using ORM.
"""
from typing import List, Dict, Tuple, Any
import logging
from ..repositories.picklist_repository import PicklistRepository
from ..repositories.batch_pick_sequence_repository import BatchPickSequenceRepository
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import PICKER_LOCATIONS

# Create logger
logger = logging.getLogger(__name__)

class BatchPickSequenceService:
    """Service for handling pick sequence updates."""
    
    def __init__(self):
        """Initialize the service with repositories."""
        self.picklist_repo = PicklistRepository()
        self.batch_pick_sequence_repo = BatchPickSequenceRepository()
        self.route_optimizer = RouteOptimizer()
    
    def update_pick_sequences(
        self,
        final_solution: List[int],
        picklistids: List[int],
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]],
        read_only: bool = False
    ) -> None:
        """
        Update pick sequences based on optimization results.
        
        Args:
            final_solution: List of picker assignments
            picklistids: List of picklist IDs
            orders_assign: List of order locations
            picktasks: List of picktask IDs
            stage_result: Dictionary of staging locations
            read_only: If True, prevents the operation
        """
        if read_only:
            logger.warning("Attempted to update pick sequences in read-only mode")
            return
        
        try:
            # Get optimized routes
            _, routes, assignments = self.route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS,
                final_solution,
                orders_assign,
                picktasks,
                stage_result
            )
            
            # Prepare sequence updates
            updates = []
            
            # Process each route
            for route in routes:
                picker_id = route.picker_id
                batch_id = f"BATCH_{picker_id}"
                
                # Delete existing sequences for this batch
                self.batch_pick_sequence_repo.delete_sequences_by_batch(batch_id, read_only=read_only)
                
                # Create new sequences
                for seq_idx, order_idx in enumerate(route.assigned_orders):
                    picktask_id = picktasks[order_idx]
                    
                    # Add to updates list
                    updates.append({
                        "batchid": batch_id,
                        "picktaskid": picktask_id,
                        "sequence": seq_idx + 1  # 1-based sequence
                    })
                    
                    logger.debug(f"Prepared sequence: Batch {batch_id}, Picktask {picktask_id}, Sequence {seq_idx + 1}")
            
            # Bulk create sequences
            if updates:
                self.batch_pick_sequence_repo.bulk_create_sequences(updates, read_only=read_only)
                logger.info(f"Successfully updated pick sequences for {len(updates)} items")
        
        except Exception as e:
            logger.error(f"Error updating pick sequences: {e}")
            raise
    
    def get_optimized_data(self, read_only: bool = True) -> Tuple[List[str], List[List[Tuple]], Dict[str, List[Tuple]], List[int]]:
        """
        Get optimized picklist data for order assignment.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            Tuple containing:
                - List[str]: Task IDs
                - List[List[Tuple]]: Locations list
                - Dict[str, List[Tuple]]: Staging locations
                - List[int]: Database IDs in order of task_keys
        """
        return self.picklist_repo.get_optimized_data(read_only=read_only)
