# Feature: Warehouse Order Picking Optimization
#   As a warehouse manager
#   I want to optimize the order picking process
#   So that I can minimize the total distance traveled by pickers

Feature: Warehouse Order Picking Optimization
  As a warehouse manager
  I want to optimize the order picking process
  So that I can minimize the total distance traveled by pickers

  Background:
    Given the warehouse has configured picker capacities
    And the warehouse has defined picker starting locations

  Scenario: Optimize picker routes using hybrid ACO-GA approach
    Given a warehouse with 2 pickers
    And a set of 5 orders to be picked
    When the ACO algorithm is run to generate initial solutions
    Then it should produce valid assignments respecting picker capacities
    When the genetic algorithm is run to optimize the solutions
    Then it should improve the solution quality
    And the final solution should respect all picker capacity constraints
    And the final solution should assign all orders to pickers

  Scenario: Visualize optimized picker routes
    Given a set of optimized picker assignments
    When the route visualization is generated
    Then each picker should have a distinct path visualization
    And the visualization should include all assigned picking locations

  Scenario: Update pick sequences in warehouse management system
    Given a set of optimized picker assignments and routes
    When the pick sequences are prepared for the warehouse management system
    Then the API payload should contain all required fields
    And the API payload should match the expected format for the warehouse system
