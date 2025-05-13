# API Integration in ForestFire

## Introduction

This document provides a comprehensive overview of the API-related components used in the ForestFire project. The project integrates with external APIs to update pick sequences in the warehouse management system after optimization. This documentation covers the HTTP client, request/response models, authentication, error handling, and best practices.

## API Components Overview

### 1. HTTP Client: HTTPX

ForestFire uses **HTTPX**, a modern, fully featured HTTP client for Python that supports both synchronous and asynchronous APIs. HTTPX is used to make API calls to the warehouse management system.

#### Key Features of HTTPX

- **Async Support**: Native support for `async`/`await` syntax
- **HTTP/2 Support**: Modern HTTP protocol support
- **Timeout Configuration**: Configurable timeouts for requests
- **SSL Verification**: Options for SSL certificate verification
- **Streaming Responses**: Support for streaming responses
- **Session Management**: Client session management

#### Usage in ForestFire

HTTPX is primarily used in the `BatchPickSequenceService` class to send optimized pick sequences to the external API:

```python
async with httpx.AsyncClient(verify=False) as client:
    response = await client.put(
        self.api_url,
        json=payload.model_dump(),
        headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "App-User-Id": "Forestfire",
            # Additional headers...
        },
        timeout=30.0,
    )
```

### 2. API Models with Pydantic

ForestFire uses **Pydantic** to define structured data models for API requests and responses. Pydantic provides data validation, serialization, and documentation capabilities.

#### Key API Models

1. **PickSequenceUpdate**
   - Represents a single pick sequence update
   - Contains information about picklist, batch, sequence, and identifiers

2. **PickTaskPayload**
   - Represents a pick task in the API payload
   - Contains task ID, user assignment, batch, and picklists

3. **PickListPayload**
   - Represents a picklist in the API payload
   - Contains picklist ID, sequence, and test information

4. **ApiPayload**
   - Top-level API payload model
   - Contains account, business unit, warehouse, and pick tasks

#### Example Model Definition

```python
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
```

### 3. API Integration Service

The `BatchPickSequenceService` class serves as the main API integration service, responsible for:

1. Transforming optimization results into API-compatible formats
2. Constructing API payloads
3. Sending requests to the external API
4. Handling responses and errors

#### Key Methods

- **`transform_updates_to_api_payload`**: Transforms internal update models to API payload format
- **`send_sequence_update`**: Sends the updates to the external API
- **`update_pick_sequences`**: Orchestrates the entire process from optimization results to API updates

## API Endpoint Details

### Batch Assign API

**Endpoint**: `https://picking-api.wms-core-pg.npaz.ohl.com/2025-18/api/picking/task/batchassign`

**Method**: PUT

**Purpose**: Updates pick sequences for batches in the warehouse management system

**Authentication**: Bearer token authentication

**Headers**:
- `Authorization`: Bearer token
- `Content-Type`: application/json
- `App-User-Id`: Application identifier
- `App-Environment`: Environment identifier
- `App-Account-id`: Account identifier
- `App-BU-Id`: Business unit identifier
- `App-WareHouse-Id`: Warehouse identifier

**Request Payload Structure**:
```json
{
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
          "Test": "PF03"
        }
      ]
    }
  ]
}
```

## Authentication and Security

### API Key Management

ForestFire uses a bearer token for API authentication:

```python
self.api_key = "1GkFdCZ6NzzbKsaTSsGY9GSFcuVZ2mrX7rnOKRQroHSQkoH0eMbU1UkkF1YtDartoVMwoVB4SyfunGCvJoaFzy7qRh_EqS_GoR39YFub"
```

**Security Considerations**:
- In production, the API key should be stored in environment variables or a secure vault
- The key should not be hardcoded in the source code
- Regular key rotation should be implemented

### SSL Verification

The current implementation disables SSL verification for development purposes:

```python
async with httpx.AsyncClient(verify=False) as client:
    # API request code
```

**Security Recommendations**:
- Enable SSL verification in production environments
- Use proper certificate validation
- Consider using certificate pinning for additional security

## Error Handling

ForestFire implements comprehensive error handling for API requests:

```python
try:
    response = await client.put(...)
    response.raise_for_status()
    logger.info("Successfully sent updates to Domain for account %s", payload.AccountId)
except httpx.RequestError as e:
    logger.error("API request failed: %s", e)
    raise
except httpx.HTTPStatusError as e:
    logger.error(
        "API returned error status: %s, Response: %s",
        e,
        e.response.text if hasattr(e, "response") else "No response",
    )
    raise
except Exception as e:
    logger.error("Error sending updates: %s", e)
    raise
```

### Error Types Handled

1. **RequestError**: Network-related errors (connection failures, timeouts)
2. **HTTPStatusError**: HTTP status errors (4xx, 5xx responses)
3. **General Exceptions**: Any other unexpected errors

## Logging and Monitoring

ForestFire implements detailed logging for API operations:

```python
logger.info("Sending API request with payload: %s", payload.model_dump())
response = await client.put(...)
logger.info("API response status: %s", response.status_code)
```

### Logging Best Practices

- Log request payloads for debugging (sanitize sensitive data)
- Log response status codes
- Log detailed error information
- Use appropriate log levels (INFO, ERROR, DEBUG)

## Testing API Integration

The ForestFire project includes tests for API integration using mocking:

```python
@pytest.mark.asyncio
async def test_send_sequence_update(self):
    # Arrange
    service = BatchPickSequenceService()
    updates = [MagicMock()]
    mock_api_data = [{"key": "value"}]
    
    # Mock the transform method
    with patch.object(service, "transform_updates_to_api_payload") as mock_transform, \
         patch("httpx.AsyncClient.put") as mock_put:
        mock_transform.return_value = mock_api_data
        
        # Mock the httpx response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_put.return_value = mock_response
        
        # Act
        await service.send_sequence_update(updates)
        
        # Assert
        mock_transform.assert_called_once_with(updates)
        mock_put.assert_called_once()
```

### Testing Approaches

1. **Unit Testing**: Mock external API calls
2. **Integration Testing**: Test against a staging API
3. **Contract Testing**: Verify API contract compliance

## Best Practices for API Integration

### 1. Separation of Concerns

- Keep API client code separate from business logic
- Use models to represent API data structures
- Implement service classes for API integration

### 2. Error Handling

- Implement comprehensive error handling
- Log detailed error information
- Provide meaningful error messages
- Consider retry mechanisms for transient failures

### 3. Configuration Management

- Store API endpoints in configuration
- Use environment variables for sensitive information
- Support different environments (development, staging, production)

### 4. Performance Optimization

- Use connection pooling
- Implement request timeouts
- Consider rate limiting
- Use asynchronous requests for better performance

### 5. Security

- Secure API keys and credentials
- Enable SSL verification
- Validate input data
- Sanitize logged information

## Future Improvements

1. **API Key Management**: Move API keys to environment variables or a secure vault
2. **Retry Mechanism**: Implement exponential backoff for failed requests
3. **Circuit Breaker**: Add circuit breaker pattern for API resilience
4. **API Versioning**: Support multiple API versions
5. **Response Caching**: Implement caching for appropriate endpoints
6. **Metrics Collection**: Add metrics for API performance monitoring

## Conclusion

The ForestFire project implements a robust API integration using modern Python libraries like HTTPX and Pydantic. The implementation follows good practices for error handling, logging, and data validation. Future improvements could focus on security, resilience, and performance optimization.

By following the patterns and practices outlined in this documentation, developers can maintain and extend the API integration capabilities of the ForestFire project effectively.
