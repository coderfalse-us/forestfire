"""
Module defining the main application for the warehouse optimization API.
This module initializes the Litestar application and includes the
OptimizationController for handling optimization requests and health checks.
"""

from litestar import Litestar
from .controller import OptimizationController

app = Litestar(route_handlers=[OptimizationController], debug=True)
