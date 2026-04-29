# payment-flow Specification

## Purpose
TBD - created by archiving change implement-stripe-checkout. Update Purpose after archive.
## Requirements
### Requirement: Conditional Payment Redirection
The system SHALL determine if a booking requires immediate payment based on the selected services and redirect the user accordingly.

#### Scenario: All services are POST-PAID
- **GIVEN** a user selects only services with `payment_model="POST-PAID"`
- **WHEN** the booking is submitted
- **THEN** the backend SHALL set the booking status to `CONFIRMED`
- **AND** the API SHALL return `payment_required: false`
- **AND** the frontend SHALL display the local success message

#### Scenario: At least one service is PRE-PAID
- **GIVEN** a user selects at least one service with `payment_model="PRE-PAID"`
- **WHEN** the booking is submitted
- **THEN** the backend SHALL set the booking status to `PENDING`
- **AND** the backend SHALL create a Stripe Checkout Session
- **AND** the API SHALL return `payment_required: true` and a `checkout_url`
- **AND** the frontend SHALL redirect the user to the `checkout_url`

### Requirement: Landing Page Fulfillment
The Landing App SHALL provide success and cancellation landing pages to handle the user's return from Stripe, ensuring a full-page experience.

#### Scenario: Return from Stripe Success
- **GIVEN** a user successfully completes a Stripe payment
- **WHEN** they are redirected back to the Landing App `/success` page
- **THEN** the page SHALL display a confirmation message
- **AND** the user SHALL be outside the booking iframe

#### Scenario: Return from Stripe Cancel
- **GIVEN** a user cancels or backs out of a Stripe payment
- **WHEN** they are redirected back to the Landing App `/cancel` page
- **THEN** the page SHALL display a message indicating the payment was not completed
- **AND** the page SHALL provide a way to return to the booking section

