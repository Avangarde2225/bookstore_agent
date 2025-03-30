```gherkin
Feature: Retrieve User Account Information
  As a user of the system
  I want to retrieve account information for a specific user
  So that I can view their details

  Background:
    Given the API endpoint "/Account/v1/User/{UUID}" with HTTP method "GET"

  Scenario: Retrieve user account information successfully
    Given a valid UUID "123456"
    When a GET request is sent to "/Account/v1/User/123456"
    Then the response status code should be 200
    And the response body should contain user details

  Scenario: Attempt to retrieve user account information with invalid UUID
    Given an invalid UUID "invalid"
    When a GET request is sent to "/Account/v1/User/invalid"
    Then the response status code should be 404
    And the response body should contain an error message

  Scenario Outline: Retrieve user account information with different UUIDs
    Given a <UUID>
    When a GET request is sent to "/Account/v1/User/<UUID>"
    Then the response status code should be <status>

    Examples:
      | UUID    | status |
      | 123456  | 200    |
      | 987654  | 200    |

  Scenario: Attempt to retrieve user account information with missing UUID
    Given no UUID provided
    When a GET request is sent to "/Account/v1/User/"
    Then the response status code should be 400
    And the response body should contain a missing parameter error message
```