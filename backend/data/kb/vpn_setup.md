# vpn_setup

## VPN Installation and Configuration
Follow these steps to connect to the corporate network securely from home.

## Prerequisites
*   You must have an active Multi-Factor Authentication (MFA) application set up on your mobile phone (Microsoft Authenticator).
*   An active internet connection.

## Installation Steps
1.  Download the **FortiClient VPN Client** from the employee portal.
2.  Install the package on your computer (supports Windows and macOS).
3.  Open FortiClient and configure a new SSL-VPN connection:
    *   **Connection Name**: Corporate VPN
    *   **Remote Gateway**: `vpn.company.com`
    *   **Port**: 10443
4.  Click "Save".

## Login Protocol
*   Enter your company username and password.
*   When prompted for MFA, open your authenticator app and approve the request.
*   Once connected, your traffic will be routed securely through the corporate gateway.
