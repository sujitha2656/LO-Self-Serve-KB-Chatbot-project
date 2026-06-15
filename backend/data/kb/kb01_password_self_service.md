# Password Self-Service Reset Guide

## Problem
Users forget their active directory passwords or get locked out of their accounts and need a quick self-service method to unlock themselves without calling the Helpdesk.

## Resolution
1. Open a browser and navigate to the self-service portal: `https://password.company.com`.
2. Click **Reset Password** or **Unlock Account**.
3. Input your corporate email address and complete the security captcha.
4. Verify your identity using one of your registered secondary MFA methods (SMS, email code, or Authenticator app approval).
5. Input a new password that matches the complexity requirements:
   - Minimum 12 characters.
   - At least 1 uppercase, 1 lowercase, 1 number, and 1 special character.
   - Cannot match any of your previous 5 passwords.
6. Submit the request and wait 2 minutes for synchronization before logging in.

## References
- See [kb02_password_expired.md](kb02_password_expired.md) if your account is fully suspended.
- Contact `identity-support@company.com` for account locks.