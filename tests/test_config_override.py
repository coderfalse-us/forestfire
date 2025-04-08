"""
This module provides a way to override configuration values for testing.
Import this module before importing any other forestfire modules to override
the configuration values.
"""
import sys
import os
from unittest.mock import patch
import builtins

# Store the original import function
original_import = builtins.__import__

# Define the configuration overrides
CONFIG_OVERRIDES = {
    'NUM_PICKERS': 3,
    'PICKER_CAPACITIES': [5, 5, 5],
    'N_POP': 10,
    'MAX_IT': 5,
    'NUM_ANTS': 3,
    'TOURNAMENT_SIZE': 2,
    'PC': 0.9,
    'PM': 0.1,
    'NM': 1,
    'NC': 2,
}

# Create a custom import function that patches the config module
def custom_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)
    
    # If this is the config module, override its values
    if name == 'forestfire.utils.config' or getattr(module, '__name__', '') == 'forestfire.utils.config':
        for key, value in CONFIG_OVERRIDES.items():
            setattr(module, key, value)
    
    return module

# Replace the built-in import function with our custom one
builtins.__import__ = custom_import
