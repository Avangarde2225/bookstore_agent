Feature: End-to-End CRUD Testing for Account API

Background:
    Given the API service is running
    And I am authenticated with valid credentials

@e2e @crud @create
Scenario: Create Account Resource
    Given I prepare test data for account creation
    When I send a POST request to "/Account/v1/Authorized" with valid data
    Then the response status code should be 200
    And I store the created account ID

@e2e @crud @read
Scenario: Read Account Resource
    Given I have a valid account ID
    When I send a GET request to "/Account/v1/User/{UUID}"
    Then the response status code should be 200
    And the response should contain valid account data

@e2e @crud @delete
Scenario: Delete Account Resource
    Given I have a valid account ID
    When I send a DELETE request to "/Account/v1/User/{UUID}"
    Then the response status code should be 200
    And the account should be deleted

@e2e @integration
Scenario: Account Integration with Other Resources
    Given I have valid credentials
    And I am authenticated

    # BookStore Integration
    When I create a new bookstore resource
    Then I can associate it with account
    And I can verify the association

    # Cleanup
    When I remove all created resources
    Then all resources should be properly cleaned up
