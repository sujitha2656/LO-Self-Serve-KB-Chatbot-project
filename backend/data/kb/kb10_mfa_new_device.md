# Registering a New Device for MFA

## Problem
Users who have purchased a new mobile phone need to transfer their Microsoft Authenticator profile to continue logging in.

## Resolution
1. On your laptop, open a browser and log in to `https://mysignins.microsoft.com/security-info`.
2. Complete the authentication challenge using your old phone.
3. Click **Add sign-in method** and select **Authenticator app**.
4. Install Microsoft Authenticator on your new phone.
5. Follow the prompts on your laptop to scan the QR code using the new device's authenticator app.
6. Once the new device is confirmed, click **Delete** next to your old device registration in the web portal to revoke its access keys.

## References
- Initial enrollment: [kb09_mfa_enrollment_setup.md](kb09_mfa_enrollment_setup.md)
- Lost device resets: `security-desk@company.com`