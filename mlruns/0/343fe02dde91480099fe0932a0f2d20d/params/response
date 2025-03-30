```gherkin
Feature: Update Book Information in the BookStore

  Background:
    Given the BookStore API is available

  Scenario: Update book information successfully
    Given a valid ISBN "1234567890"
    And the book details to update
      | Field       | Value          |
      | Title       | New Title      |
      | Author      | New Author     |
      | Description | New Description |
    When a PUT request is sent to "/BookStore/v1/Books/1234567890"
    Then the response status code should be 200
    And the book information should be updated successfully

  Scenario: Update book with invalid ISBN
    Given an invalid ISBN "invalidISBN"
    And the book details to update
      | Field       | Value          |
      | Title       | New Title      |
      | Author      | New Author     |
      | Description | New Description |
    When a PUT request is sent to "/BookStore/v1/Books/invalidISBN"
    Then the response status code should be 404
    And an error message should be returned

  Scenario: Update book with missing required fields
    Given a valid ISBN "1234567890"
    And missing required book details to update
      | Field       | Value          |
      | Title       |               |
      | Author      | New Author     |
      | Description | New Description |
    When a PUT request is sent to "/BookStore/v1/Books/1234567890"
    Then the response status code should be 400
    And an error message for missing fields should be returned
```