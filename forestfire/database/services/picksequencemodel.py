"""
    Model defining pick sequence update format.
"""
from pydantic import BaseModel

class PickSequenceUpdate(BaseModel):
    """Model representing a pick sequence update"""
    picklist_id: str
    batch_id: str
    pick_sequence: int
