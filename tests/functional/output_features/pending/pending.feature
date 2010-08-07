Feature: Pending steps inside Lettuce
    As lettuce author
    In order to keep track of what scenarios are not complete
    I want to be able to mark steps as pending

    Scenario: Pending first step
        Given I have a pending step
        Then this failing step will never run

    Scenario: Pending second step
        Given I have a passing step
        Then I have a pending step
