"""
Module for defining api endpoints for warehouse optimization.
This module provides the `OptimizationController` class which handles
warehouse optimization requests and health checks.
"""

from litestar import Controller, post, get
from litestar.di import Provide
from loguru import logger
from .schemas import OptimizationRequest
from ..core import WarehouseOptimizer
from ..utils import WarehouseConfigManager


class OptimizationController(Controller):
    """Controller for warehouse optimization operations."""

    path = "/optimize"
    dependencies = {"optimizer": Provide(WarehouseOptimizer)}

    @post("/")
    async def optimize_warehouse(
        self, data: OptimizationRequest, optimizer: WarehouseOptimizer
    ) -> dict:
        """Endpoint to optimize warehouse operations based on provided data."""
        try:
            logger.info("Received optimization request with data: {}", data)
            config = WarehouseConfigManager(data)
            logger.info(
                "Starting optimization with {} pickers", config.NUM_PICKERS
            )
            final_solution = await optimizer.optimize_main(config=config)

            logger.info("Optimization completed successfully")
            return {
                "status": "success",
                "solution": [int(x) for x in final_solution],
                "message": "Optimization and API updates completed",
            }
        except Exception as e:
            logger.error("Error in optimization process: {}", str(e))
            raise

    @get("/health")
    async def health_check(self) -> dict:
        """Health check endpoint to verify API status."""
        return {"status": "healthy"}

    @get()
    async def hello(self) -> str:
        """Simple endpoint for testing."""
        return "Hello World"


logger.configure(
    handlers=[
        {
            "sink": print,
            "format": (
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<red>{message}</red>"
                if "{level}" == "ERROR"
                else "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<level>{message}</level>"
            ),
            "colorize": True,
            "level": "INFO",
            "diagnose": True,
        }
    ]
)
if __name__ == "__main__":
    import uvicorn
    from colorama import init

    init()

    uvicorn.run(
        "forestfire.api.routes:app", host="0.0.0.0", port=8000, reload=True
    )
