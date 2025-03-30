```gherkin
Feature: Retrieve Books from the BookStore API

  Background:
    Given the BookStore API is available

  Scenario: Retrieve all books successfully
    When a GET request is sent to "/BookStore/v1/Book"
    Then the response status code should be 200
    And the response body should contain a list of books

  Scenario: Retrieve books with specific parameters
    Given there are books available in the BookStore
    When a GET request is sent to "/BookStore/v1/Book" with parameters
      | parameter   | value |
      | genre       | Fiction |
    Then the response status code should be 200
    And the response body should contain books of the specified genre

  Scenario: Handle invalid parameters
    When a GET request is sent to "/BookStore/v1/Book" with invalid parameters
    Then the response status code should be 400
    And the response body should contain an error message

  Scenario: Handle empty response
    Given there are no books available in the BookStore
    When a GET request is sent to "/BookStore/v1/Book"
    Then the response status code should be 404
    And the response body should contain a message indicating no books found
```