"""
Model defining pick sequence update format.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PickSequenceUpdate(BaseModel):
    """Model representing a pick sequence update"""

    picklist_id: str = Field(..., description="Unique id for picklist")
    batch_id: str = Field(..., description="Batch identifier")
    pick_sequence: int = Field(
        ..., ge=1, description="Sequence number for picking"
    )
    picktask_id: str = Field(..., description="Pick task identifier")
    account_id: str = Field(..., description="Account identifier")
    business_unit_id: str = Field(..., description="Business unit identifier")
    warehouse_id: str = Field(..., description="Warehouse identifier")

    class Config:
        frozen = True


class PickTaskPayload(BaseModel):
    """Pydantic model for pick task API payload"""

    task_id: str = Field(..., alias="TaskId")
    user_assigned: str = Field(default="BOB", alias="UserAssigned")
    batch_id: str = Field(..., alias="Batch")
    additional_properties: Dict[str, Any] = Field(
        default_factory=dict, alias="AdditionalProperties"
    )
    pick_lists: List["PickListPayload"] = Field(..., alias="PickLists")

    class Config:
        from_attributes = True


class PickListPayload(BaseModel):
    """Pydantic model for picklist API payload"""

    picklist_id: str = Field(..., alias="PickListId")
    pick_sequence: int = Field(..., alias="Sequence")
    test: str = Field(default="PF03", alias="Test")

    class Config:
        from_attributes = True


class ApiPayload(BaseModel):
    """Pydantic model for the complete API payload"""

    account_id: str = Field(..., alias="AccountId")
    business_unit_id: str = Field(..., alias="BusinessunitId")
    warehouse_id: str = Field(..., alias="WarehouseId")
    pick_tasks: List[PickTaskPayload] = Field(..., alias="PickTasks")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "AccountId": "ACC123",
                "BusinessunitId": "BU123",
                "WarehouseId": "WH123",
                "PickTasks": [
                    {
                        "TaskId": "TASK123",
                        "UserAssigned": "BOB",
                        "Batch": "BATCH_0",
                        "AdditionalProperties": {},
                        "PickLists": [
                            {
                                "PickListId": "PL123",
                                "Sequence": 1,
                                "Test": "PF03",
                            }
                        ],
                    }
                ],
            }
        }
