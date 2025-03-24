from typing import List, Dict
import logging
from .picklist import PicklistRepository

logger = logging.getLogger(__name__)

class BatchService:
    """Service for handling batch-related database operations"""
    
    def __init__(self):
        self.picklist_repo = PicklistRepository()
        
    def update_batch_assignments(
        self,
        final_solution: List[int],
        picklistids: List[str]
    ) -> None:
        """
        Update batch IDs for picktasks based on optimization results
        
        Args:
            final_solution: List of picker assignments
            picklistids: List of picktask IDs
        """
        try:
            # Prepare batch updates
            updates = []
            
            # Create update queries for each assignment
            for item_idx, picker_id in enumerate(final_solution):
                batch_id = f"BATCH_{picker_id}"
                picklist_id = picklistids[item_idx]
                
                query = """
                SET search_path TO nifiapp;
                UPDATE picklist 
                SET batchid = %s 
                WHERE id = %s;
                """
                updates.append((query, (batch_id, picklist_id)))
                logger.debug(f"Prepared update: Batch {batch_id} for picklist {picklist_id}")

            # Execute all updates in a single transaction
            self.picklist_repo.baserepository.execute_transaction(updates)
            logger.info(f"Successfully updated batch assignments for {len(final_solution)} items")
            
            
        except Exception as e:
            logger.error(f"Error updating batch assignments: {e}")
            raise