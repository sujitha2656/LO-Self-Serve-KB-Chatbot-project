# FortiClient VPN Installation and Setup

## Problem
Remote workers need secure access to corporate network files, databases, and intranet sites from off-site locations.

## Resolution
1. Open the **Company Portal** app on your Windows or Mac laptop.
2. Search for **FortiClient VPN** and click **Install**.
3. Once the installation is complete, launch FortiClient.
4. Click on **Configure VPN** and configure these settings:
   - **VPN Type**: SSL-VPN
   - **Connection Name**: Corporate Network
   - **Description**: Secure Gateway
   - **Remote Gateway**: `vpn.company.com`
   - **Port**: 10443
   - **Client Certificate**: None
   - **Authentication**: Prompt for Login
5. Click **Save**.
6. Enter your corporate email and password, then approve the Microsoft Authenticator push notification on your mobile phone to connect.

## References
- Troubleshooting guide: [kb04_vpn_troubleshooting.md](kb04_vpn_troubleshooting.md)
- Network team contact: `network-alerts@company.com`