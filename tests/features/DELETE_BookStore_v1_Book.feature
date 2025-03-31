Feature: DELETE /BookStore/v1/Book API Endpoint

  As an API client
  I want to interact with the /BookStore/v1/Book endpoint
  So that I can delete resources

  Background:
    Given the API service is running
    And I have valid authentication credentials


  @validation
  Scenario: Successful response validation
    Given I am making a DELETE request to "/BookStore/v1/Book"
    When I send the request with valid data
    Then the response status code should be 200
    And the response should contain valid data
    And the response should match the expected schema

