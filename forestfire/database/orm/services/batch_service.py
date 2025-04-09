"""
Service for handling batch-related operations using ORM.
"""
from typing import List, Dict, Any
import logging
from ..repositories.picklist_repository import PicklistRepository
from ..repositories.batch_pick_sequence_repository import BatchPickSequenceRepository

# Create logger
logger = logging.getLogger(__name__)

class BatchService:
    """Service for handling batch-related operations."""
    
    def __init__(self):
        """Initialize the service with repositories."""
        self.picklist_repo = PicklistRepository()
        self.batch_pick_sequence_repo = BatchPickSequenceRepository()
    
    def update_batch_assignments(
        self,
        final_solution: List[int],
        picklistids: List[int],
        read_only: bool = False
    ) -> None:
        """
        Update batch IDs for picktasks based on optimization results.
        
        Args:
            final_solution: List of picker assignments
            picklistids: List of picklist IDs
            read_only: If True, prevents the operation
        """
        if read_only:
            logger.warning("Attempted to update batch assignments in read-only mode")
            return
        
        try:
            # Prepare batch updates
            updates = []
            
            # Create update queries for each assignment
            for item_idx, picker_id in enumerate(final_solution):
                batch_id = f"BATCH_{picker_id}"
                picklist_id = picklistids[item_idx]
                
                # Add to updates list
                updates.append({
                    "id": picklist_id,
                    "data": {"batchid": batch_id}
                })
                
                logger.debug(f"Prepared update: Batch {batch_id} for picklist {picklist_id}")
            
            # Execute all updates
            for update in updates:
                self.picklist_repo.update(update["id"], update["data"], read_only=read_only)
            
            logger.info(f"Successfully updated batch assignments for {len(final_solution)} items")
        
        except Exception as e:
            logger.error(f"Error updating batch assignments: {e}")
            raise
