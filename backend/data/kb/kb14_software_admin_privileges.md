# Software Local Admin Privilege Request Policy

## Problem
Users attempting to configure custom tools encounter User Account Control (UAC) prompts requesting admin credentials.

## Resolution
*   **Standard Rule**:
    - Permanent local admin rights are restricted for security reasons. All requests require strict business justification.
*   **Short-term Admin Elevation**:
    1. Open the portal: `https://privilege.company.com`.
    2. Input your workstation asset tag and reason for elevation (e.g. "Updating Python package paths").
    3. Click **Request 2-Hour Elevation**.
    4. Once approved by security rules, log out and log back in to activate the administrator rights.

## References
- Portal catalog: [kb13_software_company_portal.md](kb13_software_company_portal.md)
- Security policy team: `infosec-group@company.com`