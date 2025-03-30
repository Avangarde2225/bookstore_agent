```gherkin
Feature: Manage Books in the BookStore

  Background:
    Given the BookStore API is available

  Scenario: Add a new book to the BookStore
    Given a valid book payload
    When a POST request is sent to "/BookStore/v1/Books" with the book details
    Then the response status code should be 201
    And the response should contain the newly added book details

  Scenario: Add a book with missing required fields
    Given an incomplete book payload
    When a POST request is sent to "/BookStore/v1/Books" with the incomplete book details
    Then the response status code should be 400
    And the response should indicate the missing fields

  Scenario: Add a book with invalid data
    Given an invalid book payload
    When a POST request is sent to "/BookStore/v1/Books" with the invalid book details
    Then the response status code should be 422
    And the response should provide details on the validation errors

  Scenario: Add a duplicate book
    Given an existing book in the BookStore
    When a POST request is sent to "/BookStore/v1/Books" with the same book details
    Then the response status code should be 409
    And the response should indicate that the book already exists
```