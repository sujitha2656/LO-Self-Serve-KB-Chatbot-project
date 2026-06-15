# outlook_setup

## Outlook Profile and Email Sync Guide
This article helps configure Microsoft Outlook for company email sync.

## Auto-Discovery Configuration (Recommended)
1.  Open Microsoft Outlook on your machine.
2.  If this is your first time opening Outlook, it will prompt for an email address. Otherwise, go to File > Add Account.
3.  Enter your company email address (e.g., `user@company.com`) and click Connect.
4.  A login prompt from Microsoft 365 will appear. Enter your password and complete the MFA challenge.
5.  Once verified, click Done. Restart Outlook to allow your mailbox to sync.

## Manual Configuration (Fallback)
If auto-discovery fails, use these settings:
*   **Account Type**: Office 365 / Microsoft Exchange
*   **Server**: `outlook.office365.com`
*   **Port**: 443 (SSL/TLS enabled)
*   **Authentication**: OAuth2 / Modern Auth
