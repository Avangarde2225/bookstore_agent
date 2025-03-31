```gherkin
Feature: Delete Books from BookStore

  Background:
    Given the BookStore API is available

  Scenario: Delete a book successfully
    Given a valid book ID "123"
    When a DELETE request is sent to "/BookStore/v1/Books/123"
    Then the book with ID "123" is deleted successfully

  Scenario: Attempt to delete a non-existing book
    Given a non-existing book ID "999"
    When a DELETE request is sent to "/BookStore/v1/Books/999"
    Then the response status code is 404
    And the response message indicates the book does not exist

  Scenario: Delete a book with invalid ID format
    Given an invalid book ID format "abc"
    When a DELETE request is sent to "/BookStore/v1/Books/abc"
    Then the response status code is 400
    And the response message indicates an invalid ID format

  Scenario: Delete a book with unauthorized access
    Given a valid book ID "456"
    And the user is not authorized
    When a DELETE request is sent to "/BookStore/v1/Books/456"
    Then the response status code is 401
    And the response message indicates unauthorized access

  Scenario Outline: Delete multiple books
    Given the following book IDs exist:
      | Book ID |
      | 111     |
      | 222     |
      | 333     |
    When DELETE requests are sent to "/BookStore/v1/Books/<Book ID>"
    Then all specified books are deleted successfully

  Examples:
    | Book ID |
    | 111     |
    | 222     |
    | 333     |
```