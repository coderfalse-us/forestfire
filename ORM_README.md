# SQLAlchemy ORM Implementation

This document explains the SQLAlchemy ORM implementation for the Forest Fire Optimization project.

## Overview

The ORM (Object-Relational Mapping) implementation provides a safer and more structured way to interact with the database. Key features include:

- **Read-only sessions** by default to prevent accidental database modifications
- **Type safety** through SQLAlchemy models
- **Repository pattern** for clean separation of concerns
- **Explicit write operations** that require opting out of read-only mode

## Directory Structure

```
forestfire/database/orm/
├── __init__.py                  # Package initialization
├── base.py                      # Base configuration and session management
├── models.py                    # SQLAlchemy models
├── repository.py                # Base repository class
├── repositories/                # Repository implementations
│   ├── __init__.py
│   ├── picklist_repository.py
│   └── batch_pick_sequence_repository.py
└── services/                    # Service implementations
    ├── __init__.py
    ├── batch_service.py
    └── batch_pick_sequence_service.py
```

## Key Components

### 1. Base Configuration (`base.py`)

This module provides:

- Database connection configuration
- Session factories for both regular and read-only sessions
- Context managers for session handling
- Database initialization functions

### 2. Models (`models.py`)

SQLAlchemy models that map to database tables:

- `Warehouse`: Maps to `synob_tabr.warehouses` table
- `Picklist`: Maps to `nifiapp.picklist` table
- `BatchPickSequence`: Maps to `nifiapp.batch_pick_sequence` table
- `Picker`: Maps to `nifiapp.pickers` table (if exists)

### 3. Base Repository (`repository.py`)

A generic repository class that provides:

- Common database operations (get, find, create, update, delete)
- Read-only enforcement by default
- Custom query execution

### 4. Repository Implementations (`repositories/`)

Specific repository implementations for each model:

- `PicklistRepository`: Operations for the `Picklist` model
- `BatchPickSequenceRepository`: Operations for the `BatchPickSequence` model

### 5. Service Implementations (`services/`)

Services that use repositories to implement business logic:

- `BatchService`: Batch-related operations
- `BatchPickSequenceService`: Pick sequence operations

## Using Read-Only Sessions

All repository methods accept a `read_only` parameter that defaults to `True`. This means that by default, all operations are read-only and won't modify the database.

To perform write operations, you must explicitly set `read_only=False`:

```python
# Read operation (default)
picklist = picklist_repo.get_by_id(123)

# Write operation (explicit)
picklist_repo.update(123, {"batchid": "BATCH_1"}, read_only=False)
```

## Migration from Direct Database Access

The `migrate_to_orm.py` script helps test and validate the migration from direct database access to ORM. It compares the results of the old and new implementations to ensure they produce the same output.

To run the migration tests:

```bash
python migrate_to_orm.py --test-all
```

## Example Usage

### Reading Data

```python
from forestfire.database.orm.repositories import PicklistRepository

# Initialize repository
picklist_repo = PicklistRepository()

# Get optimized data (read-only by default)
task_keys, locations, staging, picklistids = picklist_repo.get_optimized_data()
```

### Writing Data

```python
from forestfire.database.orm.services import BatchService

# Initialize service
batch_service = BatchService()

# Update batch assignments (explicitly not read-only)
batch_service.update_batch_assignments(
    final_solution=[0, 1, 0, 2],
    picklistids=[101, 102, 103, 104],
    read_only=False
)
```

## Benefits of the ORM Implementation

1. **Safety**: Read-only by default prevents accidental database modifications
2. **Structure**: Clear separation of models, repositories, and services
3. **Maintainability**: Type hints and docstrings improve code readability
4. **Flexibility**: Easy to add new models and repositories
5. **Testability**: Easier to mock and test

## Transitioning to the ORM

To transition your code to use the ORM:

1. Replace imports from `forestfire.database.services` with imports from `forestfire.database.orm.services`
2. Add the `read_only=False` parameter when you need to perform write operations
3. Run the migration tests to ensure compatibility

For example:

```python
# Old code
from forestfire.database.services.picklist import PicklistRepository
picklist_repo = PicklistRepository()
data = picklist_repo.get_optimized_data()

# New code
from forestfire.database.orm.repositories import PicklistRepository
picklist_repo = PicklistRepository()
data = picklist_repo.get_optimized_data(read_only=True)  # Explicit, but True is the default
```
