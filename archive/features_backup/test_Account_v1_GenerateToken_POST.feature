```gherkin
Feature: GenerateToken API Endpoint
  As a user of the system
  I want to be able to generate a token for authentication
  So that I can access protected resources

  Background:
    Given the API endpoint "/Account/v1/GenerateToken" with HTTP method "POST" is available

  Scenario: Generate token successfully
    Given a valid user credentials
    When a POST request is sent to "/Account/v1/GenerateToken" with the following parameters:
      | username | password |
      | user1    | pass123  |
    Then the response status code should be 200
    And the response body should contain a valid token

  Scenario: Invalid credentials provided
    Given invalid user credentials
    When a POST request is sent to "/Account/v1/GenerateToken" with the following parameters:
      | username | password |
      | user2    | invalid  |
    Then the response status code should be 401
    And the response body should contain an error message

  Scenario: Missing username in request
    Given a request without a username
    When a POST request is sent to "/Account/v1/GenerateToken" with the following parameters:
      | password |
      | pass123  |
    Then the response status code should be 400
    And the response body should contain an error message about missing username

  Scenario: Missing password in request
    Given a request without a password
    When a POST request is sent to "/Account/v1/GenerateToken" with the following parameters:
      | username |
      | user3    |
    Then the response status code should be 400
    And the response body should contain an error message about missing password
```