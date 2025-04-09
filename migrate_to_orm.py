"""
Migration script to help transition from direct database access to ORM.

This script demonstrates how to use the new ORM-based repositories and services
instead of the old direct database access code.
"""
import logging
import argparse
from forestfire.utils.config import *
from forestfire.database.services.picklist import PicklistRepository as OldPicklistRepository
from forestfire.database.services.batch_pick_seq_service import BatchPickSequenceService as OldBatchPickSequenceService
from forestfire.database.orm.repositories.picklist_repository import PicklistRepository as NewPicklistRepository
from forestfire.database.orm.services.batch_pick_sequence_service import BatchPickSequenceService as NewBatchPickSequenceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def compare_results(old_result, new_result, name):
    """
    Compare results from old and new implementations.
    
    Args:
        old_result: Result from old implementation
        new_result: Result from new implementation
        name: Name of the function being compared
    """
    logger.info(f"Comparing results for {name}...")
    
    if type(old_result) != type(new_result):
        logger.warning(f"Result types differ: {type(old_result)} vs {type(new_result)}")
    
    if isinstance(old_result, tuple) and isinstance(new_result, tuple):
        if len(old_result) != len(new_result):
            logger.warning(f"Tuple lengths differ: {len(old_result)} vs {len(new_result)}")
        
        for i, (old_item, new_item) in enumerate(zip(old_result, new_result)):
            if type(old_item) != type(new_item):
                logger.warning(f"Item {i} types differ: {type(old_item)} vs {type(new_item)}")
            
            if isinstance(old_item, list) and isinstance(new_item, list):
                if len(old_item) != len(new_item):
                    logger.warning(f"Item {i} lengths differ: {len(old_item)} vs {len(new_item)}")
                else:
                    logger.info(f"Item {i} lengths match: {len(old_item)}")
            
            elif isinstance(old_item, dict) and isinstance(new_item, dict):
                if len(old_item) != len(new_item):
                    logger.warning(f"Item {i} lengths differ: {len(old_item)} vs {len(new_item)}")
                else:
                    logger.info(f"Item {i} lengths match: {len(old_item)}")
    
    elif isinstance(old_result, list) and isinstance(new_result, list):
        if len(old_result) != len(new_result):
            logger.warning(f"List lengths differ: {len(old_result)} vs {len(new_result)}")
        else:
            logger.info(f"List lengths match: {len(old_result)}")
    
    elif isinstance(old_result, dict) and isinstance(new_result, dict):
        if len(old_result) != len(new_result):
            logger.warning(f"Dict lengths differ: {len(old_result)} vs {len(new_result)}")
        else:
            logger.info(f"Dict lengths match: {len(old_result)}")
    
    logger.info(f"Comparison for {name} complete")

def test_picklist_repository():
    """Test and compare old and new PicklistRepository implementations."""
    logger.info("Testing PicklistRepository...")
    
    # Initialize repositories
    old_repo = OldPicklistRepository()
    new_repo = NewPicklistRepository()
    
    # Test fetch_picklist_data
    logger.info("Testing fetch_picklist_data...")
    old_result = old_repo.fetch_picklist_data()
    new_result = new_repo.fetch_picklist_data()
    compare_results(old_result, new_result, "fetch_picklist_data")
    
    # Test fetch_distinct_picktasks
    logger.info("Testing fetch_distinct_picktasks...")
    old_result = old_repo.fetch_distinct_picktasks()
    new_result = new_repo.fetch_distinct_picktasks()
    compare_results(old_result, new_result, "fetch_distinct_picktasks")
    
    # Test map_picklist_data
    logger.info("Testing map_picklist_data...")
    old_result = old_repo.map_picklist_data()
    new_result = new_repo.map_picklist_data()
    compare_results(old_result, new_result, "map_picklist_data")
    
    # Test get_optimized_data
    logger.info("Testing get_optimized_data...")
    old_result = old_repo.get_optimized_data()
    new_result = new_repo.get_optimized_data()
    compare_results(old_result, new_result, "get_optimized_data")
    
    logger.info("PicklistRepository tests complete")

def test_batch_pick_sequence_service():
    """Test and compare old and new BatchPickSequenceService implementations."""
    logger.info("Testing BatchPickSequenceService...")
    
    # Initialize services
    old_service = OldBatchPickSequenceService()
    new_service = NewBatchPickSequenceService()
    
    # Test get_optimized_data
    logger.info("Testing get_optimized_data...")
    old_result = old_service.picklist_repo.get_optimized_data()
    new_result = new_service.get_optimized_data()
    compare_results(old_result, new_result, "get_optimized_data")
    
    logger.info("BatchPickSequenceService tests complete")

def main():
    """Main function to run migration tests."""
    parser = argparse.ArgumentParser(description='Test migration from direct database access to ORM')
    parser.add_argument('--test-picklist', action='store_true', help='Test PicklistRepository')
    parser.add_argument('--test-batch-service', action='store_true', help='Test BatchPickSequenceService')
    parser.add_argument('--test-all', action='store_true', help='Test all components')
    
    args = parser.parse_args()
    
    if args.test_all or args.test_picklist:
        test_picklist_repository()
    
    if args.test_all or args.test_batch_service:
        test_batch_pick_sequence_service()
    
    if not (args.test_all or args.test_picklist or args.test_batch_service):
        parser.print_help()

if __name__ == '__main__':
    main()
