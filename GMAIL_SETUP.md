# Gmail OTP Setup Guide

This guide will help you configure Gmail to send OTP emails for password reset functionality.

## Prerequisites

- A Gmail account
- Google Account access

## Step-by-Step Setup

### 1. Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click on **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification
5. You'll need to verify your phone number

### 2. Generate App Password

1. After enabling 2-Step Verification, go back to **Security**
2. Under "Signing in to Google", click on **App passwords**
3. You may need to sign in again
4. In the "Select app" dropdown, choose **Mail**
5. In the "Select device" dropdown, choose **Other (Custom name)**
6. Enter a name like "Living Ledger" or "OTP Service"
7. Click **Generate**
8. Google will display a 16-character password (e.g., `abcd efgh ijkl mnop`)
9. **IMPORTANT**: Copy this password immediately - you won't be able to see it again!

### 3. Configure Environment Variables

1. Navigate to the `living_ledger` folder
2. Create a new file named `.env` (note the dot at the beginning)
3. Add the following content:

```env
# Gmail Configuration for OTP
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop

# Replace with your actual values:
# - GMAIL_USER: Your full Gmail address
# - GMAIL_APP_PASSWORD: The 16-character password from step 2 (remove spaces)
```

4. Replace `your-email@gmail.com` with your actual Gmail address
5. Replace `abcdefghijklmnop` with your 16-character app password (remove all spaces)

### Example `.env` File

```env
GMAIL_USER=john.doe@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

## Testing the Configuration

1. Start the Living Ledger server:
   ```bash
   python START.py
   ```

2. Go to the login page and click "Forgot Password?"

3. Enter a registered email address

4. Check your Gmail inbox for the OTP email

5. The email should arrive within a few seconds

## Troubleshooting

### OTP Not Received

1. **Check Spam Folder**: Gmail might filter the email as spam initially
2. **Verify Credentials**: Make sure your `.env` file has the correct email and app password
3. **Check Console**: Look at the terminal/console output for error messages
4. **App Password**: Ensure you're using an App Password, not your regular Gmail password

### "Invalid Credentials" Error

- Double-check that you've copied the app password correctly (no spaces)
- Make sure 2-Step Verification is enabled
- Try generating a new app password

### "Less Secure Apps" Message

- You don't need to enable "Less secure app access"
- App passwords work with 2-Step Verification enabled
- This is the secure, recommended method

### Fallback Mode

If Gmail is not configured, the system will print the OTP to the terminal/console:

```
============================================================
⚠️  Gmail not configured! OTP printed to terminal:
============================================================
📧 EMAIL: user@example.com
🔑 OTP: 123456
============================================================
```

You can still use this OTP to reset the password.

## Security Best Practices

1. **Never commit `.env` file to Git**: It's already in `.gitignore`
2. **Keep app password secret**: Don't share it with anyone
3. **Revoke unused app passwords**: Go to Google Account > Security > App passwords
4. **Use different app passwords**: Create separate ones for different applications
5. **Monitor account activity**: Check Google Account activity regularly

## Production Deployment

For production deployment (Render, Heroku, etc.):

1. Don't upload the `.env` file
2. Set environment variables in your hosting platform:
   - Render: Dashboard > Environment > Environment Variables
   - Heroku: Settings > Config Vars
3. Add both `GMAIL_USER` and `GMAIL_APP_PASSWORD` variables

## Alternative Email Services

If you prefer not to use Gmail, you can modify the `send_otp_email()` function in `api.py` to use:

- **SendGrid**: Professional email service with free tier
- **AWS SES**: Amazon's email service
- **Mailgun**: Developer-friendly email API
- **SMTP2GO**: Simple SMTP service

## Support

If you encounter issues:

1. Check the console output for detailed error messages
2. Verify your Gmail settings
3. Test with a simple Python script first
4. Check Google Account security settings

---

**Last Updated**: February 2026
**Version**: 1.0.0
