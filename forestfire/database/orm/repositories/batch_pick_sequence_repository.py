"""
Repository for BatchPickSequence model.
"""
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from ..repository import BaseRepository
from ..models import BatchPickSequence

# Create logger
logger = logging.getLogger(__name__)

class BatchPickSequenceRepository(BaseRepository[BatchPickSequence]):
    """Repository for handling batch pick sequence operations."""
    
    def __init__(self):
        """Initialize the repository with the BatchPickSequence model."""
        super().__init__(BatchPickSequence)
    
    def create_batch_pick_sequence(
        self, 
        batch_id: str, 
        picktask_id: str, 
        sequence: int,
        read_only: bool = False
    ) -> Optional[BatchPickSequence]:
        """
        Create a new batch pick sequence.
        
        Args:
            batch_id: Batch ID
            picktask_id: Picktask ID
            sequence: Sequence number
            read_only: If True, prevents the operation
            
        Returns:
            Created BatchPickSequence instance or None if read_only is True
        """
        if read_only:
            logger.warning(f"Attempted to create batch pick sequence in read-only mode")
            return None
        
        data = {
            "batchid": batch_id,
            "picktaskid": picktask_id,
            "sequence": sequence
        }
        
        return self.create(data, read_only=read_only)
    
    def get_sequences_by_batch(self, batch_id: str, read_only: bool = True) -> List[BatchPickSequence]:
        """
        Get all sequences for a batch.
        
        Args:
            batch_id: Batch ID
            read_only: If True, uses a read-only session
            
        Returns:
            List of BatchPickSequence instances
        """
        return self.find_by({"batchid": batch_id}, read_only=read_only)
    
    def delete_sequences_by_batch(self, batch_id: str, read_only: bool = False) -> int:
        """
        Delete all sequences for a batch.
        
        Args:
            batch_id: Batch ID
            read_only: If True, prevents the operation
            
        Returns:
            Number of deleted sequences or 0 if read_only is True
        """
        if read_only:
            logger.warning(f"Attempted to delete sequences for batch {batch_id} in read-only mode")
            return 0
        
        def transaction_func(session: Session) -> int:
            result = session.query(BatchPickSequence).filter(
                BatchPickSequence.batchid == batch_id
            ).delete()
            return result
        
        try:
            return self.execute_transaction(transaction_func, read_only=read_only) or 0
        except Exception as e:
            logger.error(f"Error deleting sequences for batch {batch_id}: {e}")
            raise
    
    def bulk_create_sequences(
        self, 
        sequences: List[Dict[str, Any]], 
        read_only: bool = False
    ) -> List[BatchPickSequence]:
        """
        Create multiple batch pick sequences.
        
        Args:
            sequences: List of dictionaries with batchid, picktaskid, and sequence
            read_only: If True, prevents the operation
            
        Returns:
            List of created BatchPickSequence instances or empty list if read_only is True
        """
        return self.bulk_create(sequences, read_only=read_only)
