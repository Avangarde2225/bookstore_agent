Feature: End-to-End CRUD Testing for BookStore API

Background:
    Given the API service is running
    And I am authenticated with valid credentials

@e2e @crud @create
Scenario: Create BookStore Resource
    Given I prepare test data for bookstore creation
    When I send a POST request to "/BookStore/v1/Books" with valid data
    Then the response status code should be 200
    And I store the created bookstore ID

@e2e @crud @read
Scenario: Read BookStore Resource
    Given I have a valid bookstore ID
    When I send a GET request to "/BookStore/v1/Books"
    Then the response status code should be 200
    And the response should contain valid bookstore data

@e2e @crud @update
Scenario: Update BookStore Resource
    Given I have a valid bookstore ID
    And I prepare updated data for bookstore
    When I send a PUT request to "/BookStore/v1/Books/{ISBN}"
    Then the response status code should be 200
    And the bookstore should be updated

@e2e @crud @delete
Scenario: Delete BookStore Resource
    Given I have a valid bookstore ID
    When I send a DELETE request to "/BookStore/v1/Books"
    Then the response status code should be 200
    And the bookstore should be deleted

@e2e @integration
Scenario: BookStore Integration with Other Resources
    Given I have valid credentials
    And I am authenticated

    # Account Integration
    When I create a new account resource
    Then I can associate it with bookstore
    And I can verify the association

    # Cleanup
    When I remove all created resources
    Then all resources should be properly cleaned up
