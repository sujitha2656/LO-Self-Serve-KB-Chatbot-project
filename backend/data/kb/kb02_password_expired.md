# Dealing with Expired Passwords

## Problem
Passwords expire every 90 days. If a user fails to update it, they are locked out of their workstation and email services, resulting in authentication failures.

## Resolution
1. If your password has expired, you cannot log in to your workstation directly if it is offline. Connect your laptop to a wired office network port or use home Wi-Fi.
2. If at login screen, click **Sign-in options** and choose security questions if configured.
3. Otherwise, use a secondary device (e.g. mobile phone) and go to the web portal: `https://portal.office.com`.
4. Try logging in; Microsoft 365 will display an alert: "Your password has expired. Update it now."
5. Enter your old password, then choose a new password.
6. Once updated on the cloud, connect your laptop to the company VPN at the login screen (using the FortiClient pre-login connection button) to sync your local workstation password with active directory.

## References
- See [kb01_password_self_service.md](kb01_password_self_service.md) for self-service guidelines.
- Contact Helpdesk at `ext. 5555` if you cannot reset it online.