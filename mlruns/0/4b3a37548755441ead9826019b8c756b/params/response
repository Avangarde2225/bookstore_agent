```gherkin
Feature: Account Authorization API Endpoint

  Background:
    Given the API endpoint "/Account/v1/Authorized" with HTTP method "POST"

  Scenario: Successful authorization request
    Given a valid user token
    When the request is sent to authorize the account
    Then the response status code should be 200
    And the response body should contain the authorized account details

  Scenario: Missing user token in the request
    Given the user token is missing
    When the request is sent to authorize the account
    Then the response status code should be 400
    And the response body should contain an error message about missing token

  Scenario Outline: Invalid user token scenarios
    Given an invalid user token "<token>"
    When the request is sent to authorize the account
    Then the response status code should be 401
    And the response body should contain an error message about invalid token

    Examples:
      | token       |
      | invalidToken1 |
      | invalidToken2 |

  Scenario: Unauthorized account authorization
    Given a valid user token
    And the account is not authorized
    When the request is sent to authorize the account
    Then the response status code should be 403
    And the response body should contain an error message about unauthorized access
```