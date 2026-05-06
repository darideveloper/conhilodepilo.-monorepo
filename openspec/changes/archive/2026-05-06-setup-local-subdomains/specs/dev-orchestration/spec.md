## MODIFIED Requirements
### Requirement: Local dev.sh script
The system SHALL provide a shell script `dev.sh` in the project root to start all development services, use `tmux` to multiplex the terminal session, and manage port tunneling for local development using `portless`.

#### Scenario: Running `dev.sh` with Portless Tunneling
- **Given** the user is in the project root and `portless` is available.
- **When** they run `./dev.sh`.
- **Then** the `tmux` session `conhilorepilo_dev` is created or attached.
- **And** the Django dashboard is started using `portless dashboard.conhilodepilo`.
- **And** the booking and landing frontends are started using their respective nested subdomains (`booking.conhilodepilo.localhost` and `conhilodepilo.localhost`).