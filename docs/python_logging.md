# Python Logging: A Comprehensive Guide

## Introduction

Logging is a critical aspect of software development that provides insights into application behavior, helps with debugging, and creates an audit trail of application activities. This document provides an overview of Python logging options, with a special focus on Loguru, which is the logging library used in the ForestFire project.

## Python Logging Options

### 1. Standard Library Logging

Python's built-in `logging` module provides a flexible framework for emitting log messages from applications:

**Key Features:**
- Part of the standard library
- Hierarchical loggers
- Multiple output handlers
- Configurable formatting
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Limitations:**
- Complex configuration
- Verbose setup code
- Limited formatting options
- No built-in support for structured logging

**Example:**
```python
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Create logger
logger = logging.getLogger(__name__)

# Use logger
logger.info("Application started")
logger.error("An error occurred: %s", error_message)
```

### 2. Third-Party Logging Libraries

Several third-party libraries extend Python's logging capabilities:

#### a. Structlog

**Key Features:**
- Structured logging
- Context binding
- Flexible output formats (JSON, key-value)
- Integration with standard logging

#### b. Python-json-logger

**Key Features:**
- JSON-formatted logs
- Compatible with standard logging
- Simple configuration

#### c. Logbook

**Key Features:**
- Modern API
- Thread-local context
- Multiple handlers
- Improved performance

## Loguru: The Modern Python Logger

### Overview

**Loguru** is a library that aims to make logging in Python simpler, more intuitive, and more powerful. It's designed to be a drop-in replacement for the standard logging module with a much more pleasant API.

### Key Features of Loguru

#### 1. Simplicity and Ease of Use

- **No Logger Configuration**: No need to create and configure loggers
- **No Handlers Setup**: Simplified handler configuration
- **No Formatters**: Built-in, customizable formatting
- **No Boilerplate**: Ready to use out of the box

#### 2. Advanced Features

- **Colored Output**: Automatic colorization of terminal output
- **Structured Logging**: Support for structured contextual information
- **Exception Capturing**: Detailed exception information with traceback
- **Asynchronous, Thread-Safe**: Works well in concurrent environments
- **Customizable Levels**: Define custom log levels
- **Rotation Features**: Built-in log rotation capabilities
- **Notifiers**: Email, Telegram, and other notification options

#### 3. Modern Python Support

- **String Formatting**: Uses new-style string formatting
- **Type Annotations**: Full type hint support
- **Context Variables**: Support for contextvars
- **Async Support**: Works well with async code

### Using Loguru in the ForestFire Project

The ForestFire project leverages Loguru for logging with the following configuration:

```python
from loguru import logger

# Configure logger
logger.configure(
    handlers=[
        {
            "sink": print,
            "format": "<green>{time:HH:mm:ss}</green> | "
                      "<level>{level: <8}</level> | "
                      "<red>{message}</red>"
                      if "{level}" == "ERROR"
                      else "<green>{time:HH:mm:ss}</green> | "
                      "<level>{level: <8}</level> | "
                      "<level>{message}</level>",
            "colorize": True,
            "level": "INFO",
            "diagnose": True,  # Adds traceback for errors
        }
    ]
)

# Use logger with context
with logger.contextualize(task_id="optimization"):
    logger.info("Starting optimization with {} pickers", NUM_PICKERS)
    
    # Log errors with detailed traceback
    try:
        # Code that might raise an exception
        pass
    except Exception as e:
        logger.error("Error in optimization process: {}", e)
        raise
```

### Benefits of Using Loguru in ForestFire

1. **Development Speed**: Minimal setup and configuration
2. **Readability**: Clean, colorized logs that are easy to read
3. **Contextual Information**: Task IDs and other context in logs
4. **Error Diagnosis**: Detailed exception information
5. **Flexibility**: Easy to add new log destinations
6. **Consistency**: Uniform logging across the application

## Logging Best Practices

### 1. Log Levels

Use appropriate log levels for different types of information:

- **DEBUG**: Detailed information, typically useful only for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the application is still working
- **ERROR**: Due to a more serious problem, the application has not been able to perform a function
- **CRITICAL**: A serious error indicating that the application itself may be unable to continue running

### 2. Contextual Information

Include relevant context in log messages:

```python
# Good
logger.info("Processing order {order_id} for customer {customer_id}", order_id=123, customer_id=456)

# Not as good
logger.info("Processing order")
```

### 3. Structured Logging

Use structured logging for machine-readable logs:

```python
# With Loguru
logger.bind(order_id=123, customer_id=456).info("Processing order")
```

### 4. Exception Handling

Log exceptions with full context:

```python
try:
    # Code that might raise an exception
    process_data()
except Exception as e:
    logger.exception("Error processing data: {}", e)
    # or with Loguru
    logger.error("Error processing data: {}", e)  # Loguru captures traceback automatically
```

### 5. Performance Considerations

Be mindful of logging performance:

```python
# Avoid expensive operations in log messages
if logger.level("DEBUG").enabled:
    logger.debug("Complex calculation result: {}", expensive_calculation())
```

## Common Logging Patterns

### 1. Application Entry Points

Log application startup and shutdown:

```python
logger.info("Application starting")
# Application code
logger.info("Application shutting down")
```

### 2. Function Entry and Exit

Log function entry and exit for important functions:

```python
def process_data(data_id):
    logger.debug("Starting to process data {}", data_id)
    # Processing code
    logger.debug("Finished processing data {}", data_id)
```

### 3. Error Boundaries

Log at error boundaries:

```python
try:
    # Code that might fail
    result = api_call()
except Exception as e:
    logger.error("API call failed: {}", e)
    raise
```

### 4. Performance Metrics

Log performance metrics:

```python
import time

start_time = time.time()
# Code to measure
elapsed = time.time() - start_time
logger.info("Operation completed in {:.2f} seconds", elapsed)
```

## Configuring Loguru for Different Environments

### Development Environment

```python
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            "colorize": True,
            "level": "DEBUG",
        }
    ]
)
```

### Production Environment

```python
logger.configure(
    handlers=[
        {
            "sink": "app.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            "rotation": "10 MB",
            "retention": "1 week",
            "compression": "zip",
            "level": "INFO",
        },
        {
            "sink": "errors.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            "rotation": "10 MB",
            "retention": "1 month",
            "compression": "zip",
            "level": "ERROR",
        }
    ]
)
```

### JSON Logging for Services

```python
import sys
import json

def json_formatter(record):
    record_dict = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
    }
    # Add extra attributes
    record_dict.update(record["extra"])
    return json.dumps(record_dict)

logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": json_formatter,
            "level": "INFO",
        }
    ]
)
```

## Migrating from Standard Logging to Loguru

If you're considering migrating from the standard logging module to Loguru, here's a simple guide:

### Standard Logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing %s items", num_items)
logger.error("Error: %s", error_message)
```

### Loguru Equivalent:

```python
from loguru import logger

logger.info("Processing {} items", num_items)
logger.error("Error: {}", error_message)
```

### Interoperability with Existing Code:

```python
from loguru import logger
import logging

# Redirect standard logging to loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
```

## Conclusion

Logging is a critical component of any production-ready application. Loguru provides a modern, intuitive, and powerful logging solution that simplifies the logging process while offering advanced features.

By using Loguru in the ForestFire project, we benefit from simplified setup, colorized output, contextual logging, and detailed error information, all of which contribute to better debugging, monitoring, and maintenance of the application.
