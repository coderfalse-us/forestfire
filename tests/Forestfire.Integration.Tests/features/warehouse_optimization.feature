Feature: Warehouse Order Picking Optimization End-to-End
  As a warehouse manager
  I want to optimize the order picking process and update the WMS
  So that the pickers can complete tasks efficiently

  Background:
    Given the warehouse configuration is loaded
      | num_pickers | picker_capacities |
      | 10          | 10                |

  Scenario: Direct API endpoint integration testing
    Given the API server is running
    When a request is sent to the health endpoint
    Then the API should respond with a healthy status
    When an optimization request is sent with the following configuration:
      | num_pickers | picker_capacities | warehouse_name |
      | 3           | [5, 5, 5]         | test_warehouse |
    Then the API should return a valid optimization solution
    When an invalid optimization request is sent
    Then the API should respond with an appropriate error

  Scenario: Complete optimization workflow with API integration
    Given the warehouse data is loaded from the database
    When the ACO optimization process is executed
    Then the ACO solutions should be valid
    When the genetic algorithm optimization is executed with the ACO solutions
    Then the final solution should be valid and optimized
    When the optimized routes are visualized with actual plotting logic
    Then the optimized routes should be saved to a file
    When the pick sequences are updated via API
    Then the API should respond with a success status

  Scenario: Optimization with different picker capacities
    Given the warehouse data is loaded from the database
    And the picker capacities are set to:
      | picker_id | capacity |
      | 0         | 8        |
      | 1         | 10       |
      | 2         | 10       |
      | 3         | 9        |
      | 4         | 11       |
      | 5         | 10       |
      | 6         | 10       |
      | 7         | 9        |
      | 8         | 11       |
      | 9         | 10       |
    When the complete optimization process is executed
    Then the final solution should respect picker capacity constraints
    When the pick sequences are updated via API
    Then the API should respond with a success status

  
