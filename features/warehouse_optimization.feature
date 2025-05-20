Feature: Warehouse Order Picking Optimization End-to-End
  As a warehouse manager
  I want to optimize the order picking process and update the WMS
  So that the pickers can complete tasks efficiently

  Background:
    Given the warehouse configuration is loaded
      | num_pickers | picker_capacities |
      | 10          | 10                |

  Scenario: Complete optimization workflow with API integration
    Given the warehouse data is loaded from the database
    When the ACO optimization process is executed
    Then the ACO solutions should be valid
    When the genetic algorithm optimization is executed with the ACO solutions
    Then the final solution should be valid and optimized
    When the optimized routes are visualized
    And the pick sequences are updated via API
    Then the API should respond with a success status

  Scenario: Optimization with different picker capacities
    Given the warehouse data is loaded from the database
    And the picker capacities are set to:
      | picker_id | capacity |
      | 0         | 8        |
      | 1         | 12       |
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

  Scenario: Handle API errors gracefully
    Given the warehouse data is loaded from the database
    When the complete optimization process is executed
    And the API endpoint is unavailable
    When the pick sequences are updated via API
    Then the system should handle the API error gracefully
    And provide appropriate error messages
