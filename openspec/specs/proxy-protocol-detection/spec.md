# proxy-protocol-detection Specification

## Purpose
TBD - created by archiving change fix-image-protocol-scheme. Update Purpose after archive.
## Requirements
### Requirement: Proxy Protocol Detection
The Dashboard SHALL correctly identify the original request protocol when running behind a reverse proxy.

#### Scenario: Secure URI Generation behind Proxy
- **Given** the Dashboard is running behind a proxy with SSL termination
- **And** the proxy sends `X-Forwarded-Proto: https`
- **When** an absolute URI is generated (e.g., for a media file)
- **Then** the URI SHALL use the `https://` scheme.

