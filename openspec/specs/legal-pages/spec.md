# legal-pages Specification

## Purpose
TBD - created by archiving change create-legal-documents-es. Update Purpose after archive.
## Requirements
### Requirement: Spanish Privacy Policy
The system SHALL provide a Privacy Policy page in Spanish at `/politica-de-privacidad` on the landing site.

#### Scenario: User visits Privacy Policy
- **GIVEN** a user navigating the landing page
- **WHEN** they click on "Política de Privacidad"
- **THEN** they SHALL be taken to a page detailing data handling practices in Spanish.

### Requirement: Spanish Terms of Service
The system SHALL provide a Terms of Service page in Spanish at `/terminos-y-condiciones` on the landing site.

#### Scenario: User visits Terms of Service
- **GIVEN** a user navigating the landing page
- **WHEN** they click on "Términos y Condiciones"
- **THEN** they SHALL be taken to a page detailing service rules in Spanish.

### Requirement: Legal Consent in Booking
The booking application SHALL require the user to accept the legal documents before completing a reservation.

#### Scenario: Submitting booking without consent
- **GIVEN** a user filling out the booking form
- **WHEN** they attempt to submit without checking the legal consent box
- **THEN** the form SHALL show a validation error
- **AND** submission SHALL be blocked.

#### Scenario: Submitting booking with consent
- **GIVEN** a user filling out the booking form
- **WHEN** they check the legal consent box and submit
- **THEN** the booking SHALL proceed normally.

### Requirement: Legal Page Styling
The legal pages SHALL be styled to match the landing site's light theme and brand identity.

#### Scenario: Visual consistency
- **GIVEN** a legal page (Privacy Policy or Terms of Service)
- **THEN** it SHALL use the site's default light background
- **AND** headings SHALL use brand colors (`brand-primary` for H1, `brand-secondary` for H2)
- **AND** bold text SHALL be highlighted with the `brand-primary` color.

