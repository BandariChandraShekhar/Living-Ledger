# Indian Standard Time (IST) Implementation

This document explains how IST timezone is implemented throughout The Living Ledger application.

## Overview

All timestamps in the application are stored and displayed in **Indian Standard Time (IST)**, which is UTC+5:30.

## Backend Implementation

### Database Layer (`database.py`)

```python
import pytz

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def get_ist_timestamp():
    """Get current timestamp in IST as string"""
    return get_ist_time().strftime('%Y-%m-%d %H:%M:%S')
```

All database operations use `get_ist_timestamp()` to ensure consistent IST timestamps:

- User registration: `created_at`
- User approval: `approved_at`
- Login sessions: `login_time`, `logout_time`
- OTP generation: `created_at`, `expires_at`
- Admin activity: `timestamp`

### API Layer (`api.py`)

The API also uses IST for all time-sensitive operations:

```python
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)
```

#### OTP Expiration (IST)

```python
# Generate OTP with 10-minute expiration in IST
expires_at = (get_ist_time() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
db.store_otp(request.email, otp, expires_at)

# Check if OTP is expired (IST)
expires_at = datetime.strptime(otp_data["expires_at"], '%Y-%m-%d %H:%M:%S')
expires_at = IST.localize(expires_at)
if get_ist_time() > expires_at:
    # OTP expired
```

## Frontend Implementation

### Admin Dashboard (`admin.html`)

JavaScript function to format timestamps in IST:

```javascript
// Format timestamp to IST
function formatISTTime(timestamp) {
    if (!timestamp) return '-';
    
    // Parse the timestamp (assuming it's already in IST from backend)
    const date = new Date(timestamp);
    
    // Format options for IST display
    const options = {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZone: 'Asia/Kolkata'
    };
    
    return date.toLocaleString('en-IN', options) + ' IST';
}
```

#### Usage Examples

```javascript
// Pending users table
<td>${formatISTTime(user.created_at)}</td>

// Login/Logout activity
<td>${formatISTTime(session.login_time)}</td>
<td>${formatISTTime(session.logout_time)}</td>

// All users table
<td>${formatISTTime(user.created_at)}</td>
```

## Display Format

Timestamps are displayed in the following format:

```
Feb 22, 2026, 02:30:45 PM IST
```

Components:
- **Month**: Short name (Jan, Feb, Mar, etc.)
- **Day**: 2-digit (01-31)
- **Year**: 4-digit
- **Time**: 12-hour format with AM/PM
- **Timezone**: "IST" suffix for clarity

## Database Storage Format

Timestamps are stored as strings in SQLite:

```
2026-02-22 14:30:45
```

Format: `YYYY-MM-DD HH:MM:SS` (24-hour format)

## Timezone Conversion

### From UTC to IST

```python
import pytz

utc_time = datetime.utcnow()
ist_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(IST)
```

### From IST to UTC

```python
ist_time = get_ist_time()
utc_time = ist_time.astimezone(pytz.UTC)
```

## Testing IST Implementation

### 1. Check Current IST Time

```python
from database import get_ist_time, get_ist_timestamp

print(f"Current IST Time: {get_ist_time()}")
print(f"Current IST Timestamp: {get_ist_timestamp()}")
```

### 2. Verify Database Timestamps

```sql
SELECT created_at, login_time, logout_time FROM login_sessions;
```

All timestamps should be in IST (UTC+5:30).

### 3. Test OTP Expiration

1. Request password reset
2. Check console output for OTP expiration time
3. Verify it shows IST time
4. Wait 10 minutes and try to use the OTP
5. Should show "OTP expired" message

### 4. Check Admin Dashboard

1. Login as admin
2. Go to admin dashboard
3. Check all timestamps in tables
4. All should display with "IST" suffix
5. Times should match Indian timezone

## Common Issues

### Issue: Times showing in UTC

**Solution**: Ensure `pytz` is installed:
```bash
pip install pytz==2024.1
```

### Issue: Browser showing local timezone

**Solution**: JavaScript `formatISTTime()` function explicitly sets `timeZone: 'Asia/Kolkata'`

### Issue: OTP expiring immediately

**Solution**: Check that both OTP creation and validation use IST:
```python
# Creation
expires_at = (get_ist_time() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')

# Validation
expires_at = IST.localize(datetime.strptime(otp_data["expires_at"], '%Y-%m-%d %H:%M:%S'))
if get_ist_time() > expires_at:
    # Expired
```

## Dependencies

```txt
pytz==2024.1
```

Add to `requirements.txt` for deployment.

## Benefits of IST Implementation

1. **Consistency**: All timestamps use the same timezone
2. **User-Friendly**: Indian users see familiar times
3. **Accurate Logging**: Login/logout times match user expectations
4. **Reliable OTP**: Expiration times are predictable
5. **Admin Clarity**: Activity logs show correct times

## Future Enhancements

Potential improvements:

1. **User Timezone Preference**: Allow users to select their timezone
2. **Automatic Detection**: Detect user's timezone from browser
3. **Multiple Timezone Display**: Show both IST and user's local time
4. **Timezone Conversion**: Convert between timezones in UI

---

**Last Updated**: February 2026
**Version**: 1.0.0
