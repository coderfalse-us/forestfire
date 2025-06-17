"""Service for handling pick sequence updates.

This module provides functionality for updating pick sequences in the database
based on optimized routes for warehouse order picking.
"""

from typing import List, Dict, Tuple
from loguru import logger
import httpx

from .picksequencemodel import (
    PickSequenceUpdate,
    PickTaskPayload,
    PickListPayload,
    ApiPayload,
)
from .picklist import PicklistRepository
from src.optimizer.services.routing import RouteOptimizer


class BatchPickSequenceService:
    """Service for handling pick sequence updates"""

    def __init__(self):
        self.picklist_repo = PicklistRepository()
        self.route_optimizer = RouteOptimizer()
        self.api_url = (
            "https://picking-api.wms-core-pg.npaz.ohl.com/"
            "2025-26/api/picking/task/batchassign"
        )
        self.api_key = "riwKTxvgMlIiDuDRcOoXh3IwaVtci_UvFWKe_UYv4hizFhSW7Maq8xDhLCIIceIu2LGK9HCeXu8k_DCE4e52CFEEQqU0ja-Tkiyb-Myn"

    def _transform_updates_to_api_format(
        self, updates: List[PickSequenceUpdate]
    ) -> List[ApiPayload]:
        # Group updates by batch_id
        grouped_updates = {}

        for update in updates:
            # Create a key for grouping by account, business unit, and warehouse
            org_key = (
                update.account_id,
                update.business_unit_id,
                update.warehouse_id,
            )

            batch_id = update.batch_id.strip()

            # Initialize nested dictionaries if they don't exist
            if org_key not in grouped_updates:
                grouped_updates[org_key] = {}

            if batch_id not in grouped_updates[org_key]:
                grouped_updates[org_key][batch_id] = []

            # Add the picklist to the appropriate batch
            grouped_updates[org_key][batch_id].append(
                PickListPayload(
                    PickListId=update.picklist_id,
                    Sequence=update.pick_sequence,
                )
            )

        # Create the final API payload structure
        api_payload = []

        for (
            account_id,
            business_unit_id,
            warehouse_id,
        ), batches in grouped_updates.items():
            pick_tasks = []

            for batch_id, pick_lists in batches.items():
                # Use the actual picktask_id if available,
                # Find an update with this batch_id to get its picktask_id
                task_id = next(
                    (
                        u.picktask_id
                        for u in updates
                        if u.batch_id.strip() == batch_id and u.picktask_id
                    ),
                    f"{batch_id}_{len(pick_lists)}",
                )

                pick_tasks.append(
                    PickTaskPayload(
                        TaskId=task_id, Batch=batch_id, PickLists=pick_lists
                    )
                )

            api_payload.append(
                ApiPayload(
                    AccountId=account_id,
                    BusinessunitId=business_unit_id,
                    WarehouseId=warehouse_id,
                    PickTasks=pick_tasks,
                )
            )
        return api_payload

    async def send_sequence_update(
        self, updates: List[PickSequenceUpdate]
    ) -> None:
        """Send pick sequence updates to the API"""
        if not updates:
            logger.warning("No updates to send")

        # Transform the updates to the required API format
        api_payloads = self._transform_updates_to_api_format(updates)
        logger.info(
            "Transformed {} updates into API payloads", len(api_payloads)
        )

        # Disable SSL verification for development/testing
        # In production, use proper certificate verification
        async with httpx.AsyncClient(verify=False) as client:
            for payload in api_payloads:
                try:
                    logger.info(
                        "Sending API request with payload: {}",
                        payload.model_dump(),
                    )
                    response = await client.put(
                        self.api_url,
                        json=payload.model_dump(),
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "App-User-Id": "Forestfire",
                            "App-Environment": "Environment1",
                            "App-Account-id": "STB",
                            "App-BU-Id": "60176",
                            "App-WareHouse-Id": "STB",
                        },
                        timeout=30.0,
                    )
                    # Log the response for debugging
                    logger.info("API response status: {}", response.status_code)
                    response.raise_for_status()
                    logger.info(
                        "Successfully sent updates to Domain for account {}",
                        payload.AccountId,
                    )
                except httpx.RequestError as e:
                    logger.error("API request failed: {}", e)
                    raise
                except httpx.HTTPStatusError as e:
                    logger.error(
                        "API returned error status: {}, Response: {}",
                        e,
                        (
                            e.response.text
                            if hasattr(e, "response")
                            else "No response"
                        ),
                    )
                    raise
                except Exception as e:
                    logger.error("Error sending updates: {}", e)
                    raise

    async def update_pick_sequences(
        self,
        num_pickers: int,
        picker_locations: List[Tuple[float, float]],
        final_solution: List[int],
        picklistids: List[str],  # pylint: disable=unused-argument
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]],
    ) -> None:
        """Update pick sequences based on optimized routes."""
        try:
            logger.info("Starting pick sequence updates")
            logger.debug(
                "Input params - pickers: {}, solution: {}, tasks: {}",
                num_pickers,
                final_solution,
                len(picktasks),
            )
            # Get optimized routes
            # pylint: disable=unused-variable
            _, routes, assignments = (
                self.route_optimizer.calculate_shortest_route(
                    num_pickers,
                    picker_locations,
                    final_solution,
                    orders_assign,
                    picktasks,
                    stage_result,
                )
            )

            # Get all picklist-picktask relationships in one query
            query = """
            SELECT p.id, p.picktaskid, p.xcoordinate, p.ycoordinate,
            p.accountid,p.businessunitid,p.warehouseid
            FROM nifiapp.picklist p
            WHERE p.picktaskid = ANY($1);
            """
            picklist_data = (
                await self.picklist_repo.baserepository.execute_query(
                    query, (picktasks,)
                )
            )

            # Create mappings
            location_to_picklists = {}
            picktask_assignments = {
                picktasks[idx]: picker_id
                for idx, picker_id in enumerate(final_solution)
            }

            # Process all picklists and their locations
            for (
                picklist_id,
                picktask_id,
                xcoordinate,
                ycoordinate,
                accountid,
                businessunitid,
                warehouseid,
            ) in picklist_data:
                logger.info(
                    "Processing row - picklist_id: {}, coords: ({}, {})",
                    picklist_id,
                    xcoordinate,
                    ycoordinate,
                )
                if picktask_id in picktask_assignments:
                    picker_id = picktask_assignments[picktask_id]
                    batch_id = f"BATCH_{picker_id}"
                    location = ((xcoordinate), (ycoordinate))

                    if location not in location_to_picklists:
                        location_to_picklists[location] = []

                    location_to_picklists[location].append(
                        {
                            "picklist_id": picklist_id,
                            "batch_id": batch_id,
                            "picktask": picktask_id,
                            "accountid": accountid,
                            "businessunitid": businessunitid,
                            "warehouseid": warehouseid,
                        }
                    )

            # Process routes and generate updates
            updates = []
            sequence_tracking = {}

            for route in routes:
                if not route.locations:
                    continue

                batch_id = f"BATCH_{route.picker_id}"
                sequence_tracking.setdefault(batch_id, 1)
                processed_items = set()

                for loc in route.locations:
                    if loc in location_to_picklists:
                        for entry in location_to_picklists[loc]:
                            if entry["batch_id"] == batch_id:
                                item_key = (entry["picklist_id"], loc, batch_id)

                                if item_key not in processed_items:
                                    processed_items.add(item_key)
                                    seq = sequence_tracking[batch_id]
                                    updates.append(
                                        PickSequenceUpdate(
                                            picklist_id=entry["picklist_id"],
                                            batch_id=batch_id,
                                            pick_sequence=seq,
                                            picktask_id=entry["picktask"],
                                            account_id=entry["accountid"],
                                            business_unit_id=entry[
                                                "businessunitid"
                                            ],
                                            warehouse_id=entry["warehouseid"],
                                        )
                                    )
                                    sequence_tracking[batch_id] += 1

            # Execute all updates in single transaction
            if updates:
                await self.send_sequence_update(updates)
                logger.info(
                    "Sent {} picklists across {} batches",
                    len(processed_items),
                    len(sequence_tracking),
                )
            else:
                logger.warning("No updates required for pick sequences")

        except Exception as e:
            logger.error("Error updating pick sequences: {}", e, exc_info=True)
            raise
