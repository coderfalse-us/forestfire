"""Environment setup for BDD testing."""

import os
import asyncio
from unittest.mock import patch
from behave.api.async_step import use_or_create_async_context

# Import the modules we need to patch
from src.database.services.batch_pick_seq_service import (
    BatchPickSequenceService,
)
from src.plots.graph import PathVisualizer


def before_all(context):
    """Set up the environment before all tests."""
    # Set up async event loop for async steps
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    context.loop = loop

    # Store original methods for restoration
    context.original_methods = {
        "update_pick_sequences": BatchPickSequenceService.update_pick_sequences,
        "plot_routes": PathVisualizer.plot_routes,
    }

    # Set up test environment variables
    os.environ["TEST_MODE"] = "True"


def after_all(context):
    """Clean up after all tests."""
    # Restore original methods
    BatchPickSequenceService.update_pick_sequences = context.original_methods[
        "update_pick_sequences"
    ]
    PathVisualizer.plot_routes = context.original_methods["plot_routes"]

    # Clean up environment variables
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]

    # Close async event loop
    context.loop.close()


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Create or get async context for this scenario
    context = use_or_create_async_context(context)

    # Mock visualization to avoid actual plotting in tests
    def mock_plot_routes(*_args, **_kwargs):
        return None

    # Apply the mock only for visualization
    if not scenario.name.lower().startswith("complete optimization workflow"):
        # Don't mock for the main workflow test
        context.mock_plot = patch.object(
            PathVisualizer, "plot_routes", mock_plot_routes
        )
        context.mock_plot.start()


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Stop mocks if they were started
    if hasattr(context, "mock_plot"):
        context.mock_plot.stop()

    # Clear any scenario-specific attributes
    for attr in [
        "api_success",
        "api_error",
        "api_unavailable",
        "final_solution",
        "final_fitness",
        "aco_solutions",
    ]:
        if hasattr(context, attr):
            delattr(context, attr)
