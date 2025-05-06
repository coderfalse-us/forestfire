"""
    Model defining pick sequence update format.
"""
from pydantic import BaseModel

class PickSequenceUpdate(BaseModel):
    """Model representing a pick sequence update"""
    picklist_id: str
    batch_id: str
    pick_sequence: int
    picktask_id: str = None
    account_id: str = None
    business_unit_id: str = None
    warehouse_id: str = None
