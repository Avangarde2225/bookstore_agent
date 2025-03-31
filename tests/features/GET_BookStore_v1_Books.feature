Feature: GET /BookStore/v1/Books API Endpoint

  As an API client
  I want to interact with the /BookStore/v1/Books endpoint
  So that I can get resources

  Background:
    Given the API service is running
    And I have valid authentication credentials


  @validation
  Scenario: Successful response validation
    Given I am making a GET request to "/BookStore/v1/Books"
    When I send the request with valid data
    Then the response status code should be 200
    And the response should contain valid data
    And the response should match the expected schema

