```gherkin
Feature: Manage User Accounts via POST request to /Account/v1/User

  Background:
    Given the API endpoint "/Account/v1/User" with HTTP method "POST" is available

  Scenario: Create a new user account successfully
    Given a valid user payload with the following details:
      | username | email             | password |
      | testuser | testuser@email.com | password123 |
    When the request is sent to create a new user account
    Then the response status code should be 201
    And the response body should contain the user details

  Scenario: Attempt to create a user account with missing required fields
    Given an incomplete user payload with missing details:
      | username | email             |
      | testuser | testuser@email.com |
    When the request is sent to create a new user account
    Then the response status code should be 400
    And the response body should contain an error message

  Scenario: Attempt to create a user account with invalid email format
    Given a user payload with an invalid email format:
      | username | email             | password |
      | testuser | invalid_email     | password123 |
    When the request is sent to create a new user account
    Then the response status code should be 400
    And the response body should contain an error message

  Scenario: Attempt to create a user account with an existing username
    Given an existing username in the system
    And a user payload with an existing username:
      | username | email             | password |
      | existinguser | existinguser@email.com | password123 |
    When the request is sent to create a new user account
    Then the response status code should be 409
    And the response body should contain an error message
```