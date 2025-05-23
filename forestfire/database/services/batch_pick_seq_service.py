"""Service for handling pick sequence updates.

This module provides functionality for updating pick sequences in the database
based on optimized routes for warehouse order picking.
"""

from typing import List, Dict, Tuple
import logging
from .picklist import PicklistRepository
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import (
    PICKER_LOCATIONS
)

logger = logging.getLogger(__name__)

class BatchPickSequenceService:
    """Service for handling pick sequence updates"""

    def __init__(self):
        self.picklist_repo = PicklistRepository()
        self.route_optimizer = RouteOptimizer()

    def update_pick_sequences(
        self,
        final_solution: List[int],
        picklistids: List[str],  # pylint: disable=unused-argument
        orders_assign: List[List[Tuple[float, float]]],
        picktasks: List[str],
        stage_result: Dict[str, List[Tuple[float, float]]]
    ) -> None:
        try:
            # Get optimized routes
            # pylint: disable=unused-variable
            _, routes, assignments = (
                self.route_optimizer.calculate_shortest_route(

                PICKER_LOCATIONS,
                final_solution,
                orders_assign,
                picktasks,
                stage_result
            ))

            # Get all picklist-picktask relationships in one query
            query = """
            SET search_path TO nifiapp;
            SELECT p.id, p.picktaskid, p.xcoordinate, p.ycoordinate
            FROM picklist p
            WHERE p.picktaskid = ANY(%s);
            """

            picklist_data = self.picklist_repo.baserepository.execute_query(
                query, (picktasks,)
            )

            # Create mappings
            location_to_picklists = {}
            picktask_assignments = {
                picktasks[idx]: picker_id
                for idx, picker_id in enumerate(final_solution)
            }

            # Process all picklists and their locations
            for picklist_id, picktask_id, x, y in picklist_data:
                if picktask_id in picktask_assignments:
                    picker_id = picktask_assignments[picktask_id]
                    batch_id = f'BATCH_{picker_id}'
                    location = (float(x), float(y))

                    if location not in location_to_picklists:
                        location_to_picklists[location] = []

                    location_to_picklists[location].append({
                        'picklist_id': picklist_id,
                        'batch_id': batch_id,
                        'picktask': picktask_id
                    })

            # Process routes and generate updates
            updates = []
            sequence_tracking = {}

            for route in routes:
                if not route.locations:
                    continue

                batch_id = f'BATCH_{route.picker_id}'
                sequence_tracking.setdefault(batch_id, 1)
                processed_items = set()

                for loc in route.locations:
                    if loc in location_to_picklists:
                        for entry in location_to_picklists[loc]:
                            if entry['batch_id'] == batch_id:
                                item_key = (entry['picklist_id'], loc, batch_id)

                                if item_key not in processed_items:
                                    processed_items.add(item_key)
                                    updates.append((
                                        """
                                        SET search_path TO nifiapp;
                                        UPDATE picklist
                                        SET picksequence = %s, batchid = %s
                                        WHERE id = %s;
                                        """,
                                        (sequence_tracking[batch_id],
                                         batch_id,
                                         entry['picklist_id'])
                                    ))
                                    sequence_tracking[batch_id] += 1

            # Execute all updates in single transaction
            if updates:
                self.picklist_repo.baserepository.execute_transaction(updates)
                logger.info(
                    'Updated %d picklists across %d batches',
                    len(processed_items), len(sequence_tracking)
                )
            else:
                logger.warning('No updates required for pick sequences')

        except Exception as e:
            logger.error('Error updating pick sequences: %s', e, exc_info=True)
            raise
