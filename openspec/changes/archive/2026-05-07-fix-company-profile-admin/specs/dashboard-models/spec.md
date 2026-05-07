# Spec Delta: Terms and Conditions Requirement

## MODIFIED Requirements

### Requirement: Terms and Conditions Configuration
The system MUST allow an administrator to configure a Terms and Conditions URL for the company.

#### Scenario: Fetching company profile
- **WHEN** the company configuration is requested
- **THEN** the configuration MUST include a valid `terms_and_conditions_url`.
