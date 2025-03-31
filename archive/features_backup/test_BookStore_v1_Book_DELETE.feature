```gherkin
Feature: Manage books in the BookStore

  Background:
    Given the BookStore API is available

  Scenario: Delete a book successfully
    Given a book with ID "123" exists in the BookStore
    When a DELETE request is sent to "/BookStore/v1/Book/123"
    Then the book with ID "123" is deleted successfully

  Scenario: Attempt to delete a non-existing book
    Given no book with ID "999" exists in the BookStore
    When a DELETE request is sent to "/BookStore/v1/Book/999"
    Then a 404 Not Found response is returned

  Scenario: Delete a book with invalid ID
    Given an invalid book ID "abc"
    When a DELETE request is sent to "/BookStore/v1/Book/abc"
    Then a 400 Bad Request response is returned

  Scenario Outline: Delete multiple books
    Given the following books exist in the BookStore:
      | Book ID |
      | 111     |
      | 222     |
    When DELETE requests are sent to "/BookStore/v1/Book/<book_id>"
    Then the books are deleted successfully

    Examples:
      | book_id |
      | 111     |
      | 222     |

  Scenario: Delete a book with unauthorized access
    Given an unauthorized user
    When a DELETE request is sent to "/BookStore/v1/Book/123"
    Then a 401 Unauthorized response is returned
```