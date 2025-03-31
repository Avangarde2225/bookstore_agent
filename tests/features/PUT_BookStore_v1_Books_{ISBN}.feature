Feature: PUT /BookStore/v1/Books/{ISBN} API Endpoint

  As an API client
  I want to interact with the /BookStore/v1/Books/{ISBN} endpoint
  So that I can put resources

  Background:
    Given the API service is running
    And I have valid authentication credentials


  @negative @validation
  Scenario: Missing required parameters
    Given I am making a PUT request to "/BookStore/v1/Books/{ISBN}"
    When I send the request without required parameters
    Then the response status code should be 400
    And the response should indicate missing required parameters


  @validation
  Scenario: Successful response validation
    Given I am making a PUT request to "/BookStore/v1/Books/{ISBN}"
    When I send the request with valid data
    Then the response status code should be 200
    And the response should contain valid data
    And the response should match the expected schema

