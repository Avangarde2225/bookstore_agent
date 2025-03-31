Feature: POST /Account/v1/Authorized API Endpoint

  As an API client
  I want to interact with the /Account/v1/Authorized endpoint
  So that I can post resources

  Background:
    Given the API service is running
    And I have valid authentication credentials


  @validation
  Scenario: Successful response validation
    Given I am making a POST request to "/Account/v1/Authorized"
    When I send the request with valid data
    Then the response status code should be 200
    And the response should contain valid data
    And the response should match the expected schema

