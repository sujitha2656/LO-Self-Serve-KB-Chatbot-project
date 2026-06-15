# VPN Connection Troubleshooting

## Problem
Users encounter connection timeouts, authentication failures, or "Unable to resolve server" errors when attempting to connect to the corporate VPN.

## Resolution
*   **Error: Unable to resolve server (Status: 98)**:
    - Check your local internet connection. Try opening a public site (e.g. `google.com`) to confirm connectivity.
    - If your local Wi-Fi is working, restart your home router to refresh DNS leases.
*   **Error: Authentication failed or MFA timeout**:
    - Verify your password is correct by logging in to `https://portal.office.com`.
    - Ensure your mobile phone has an active cellular data or Wi-Fi connection to receive the Authenticator app push notification.
*   **VPN Disconnects frequently**:
    - Disconnect other devices on your home network that consume high bandwidth.
    - Switch from Wi-Fi to a wired Ethernet connection to stabilize latency.

## References
- Install details: [kb03_vpn_install_forticlient.md](kb03_vpn_install_forticlient.md)
- Help desk ticket hotline: `helpdesk-vpn@company.com`