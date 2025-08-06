# LXCloud v1.2.0 - New Features Guide

## Overview

LXCloud v1.2.0 introduces several key improvements requested by users:

1. **2FA Login Flow**: Users with 2FA enabled must provide their authenticator code during login
2. **Admin Auto-Redirect**: Admin users are automatically redirected to the admin panel after login
3. **Enhanced Admin Management**: Admins can now unbind screens, reset passwords, and delete users

## 🔐 Two-Factor Authentication Login Flow

### How It Works

When a user with 2FA enabled attempts to log in:

1. **Step 1**: User enters username and password
2. **Step 2**: System validates credentials
3. **Step 3**: If 2FA is enabled, system prompts for 2FA token
4. **Step 4**: User enters 6-digit code from authenticator app
5. **Step 5**: System verifies token and completes login

### Implementation Details

#### Backend Changes
```python
# Modified /api/login endpoint
if user[4]:  # two_fa_enabled
    if not two_fa_token:
        return jsonify({
            'requires_2fa': True,
            'message': 'Two-factor authentication required'
        }), 200
    
    # Verify 2FA token
    totp = pyotp.TOTP(user[5])
    if not totp.verify(two_fa_token):
        return jsonify({'error': 'Invalid 2FA token'}), 401
```

#### Frontend Changes
- Login form now shows 2FA input when required
- Seamless transition between password and 2FA steps
- Clear error messages for invalid tokens

### User Experience
- **Without 2FA**: Normal login flow (unchanged)
- **With 2FA**: Additional step for token verification
- **Invalid Token**: Clear error message with retry option

## 🎯 Admin Auto-Redirect

### How It Works

After successful login, the system checks user roles:
- **Regular Users**: Redirected to Dashboard (`/`)
- **Admin Users**: Redirected to Admin Panel (`/admin`)

### Implementation
```javascript
// In Login.js
if (result.user && (result.user.is_admin || result.user.is_administrator)) {
    navigate('/admin');
} else {
    navigate('/');
}
```

## 🛠️ Enhanced Admin Management

### New Admin Functions

#### 1. Unbind User Screens
**Purpose**: Remove all screens from a user, making them unassigned controllers

**API Endpoint**: `POST /api/admin/users/{id}/unbind-screens`

**What It Does**:
- Moves user's screens back to controllers table
- Marks controllers as unassigned
- Preserves screen data and location information
- Generates new registration keys

**Use Cases**:
- User leaving organization
- Redistributing screens
- Troubleshooting screen assignments

#### 2. Reset User Password
**Purpose**: Admin can reset any user's password

**API Endpoint**: `POST /api/admin/users/{id}/reset-password`

**Request Body**:
```json
{
  "new_password": "newpassword123"
}
```

**Restrictions**:
- Cannot reset super admin passwords
- Minimum 6 character requirement
- Admin confirmation required

**Use Cases**:
- User forgot password
- Security incident response
- Account recovery

#### 3. Delete User
**Purpose**: Permanently remove user and transfer their screens

**API Endpoint**: `DELETE /api/admin/users/{id}/delete`

**What It Does**:
- Deletes user account permanently
- Moves user's screens to unassigned controllers
- Removes all user data (cascading delete)
- Preserves screen historical data

**Restrictions**:
- Cannot delete super admin accounts
- Confirmation dialog required
- Action is irreversible

**Use Cases**:
- User left organization permanently
- Cleanup inactive accounts
- GDPR compliance requests

### Admin Panel UI Improvements

#### Enhanced User Table
- Added "Screens" column showing screen count per user
- Color-coded action buttons for different functions
- Tooltips explaining each action

#### Action Buttons
- **Blue**: Make/Remove Admin
- **Gray**: Unbind Screens (only if user has screens)
- **Yellow**: Reset Password
- **Red**: Delete User

#### Safety Features
- Confirmation dialogs for destructive actions
- Clear success/error messaging
- Auto-refresh after actions
- Protection against admin self-modification

## 🔄 Update System

### Version Information
- **App Version**: 1.2.0
- **Database Version**: 2 (unchanged)
- **Update Type**: Feature enhancement

### How to Update

#### From Existing Installation
```bash
cd LXCloud
git pull origin main
./update.sh
```

#### First Time Installation
```bash
git clone https://github.com/JeffMolenaar/LXCloud.git
cd LXCloud
./install.sh
```

### Update Script Features
- Automatic version detection
- Database backup before update
- Preserves all user data
- Service restart handling
- Rollback capability

## 🧪 Testing the New Features

### Testing 2FA Login Flow

1. **Setup 2FA for a test user**:
   - Login to user account
   - Go to Profile → 2FA Settings
   - Scan QR code with authenticator app
   - Verify and enable 2FA

2. **Test Login**:
   - Logout completely
   - Login with username/password
   - Should prompt for 2FA token
   - Enter 6-digit code from app
   - Should complete login successfully

3. **Test Invalid Token**:
   - Try login with wrong 2FA code
   - Should show error message
   - Should allow retry

### Testing Admin Features

1. **Create Test Users**:
   ```bash
   # Use admin panel or API to create test users
   # Assign some screens to test users
   ```

2. **Test Screen Unbinding**:
   - Login as admin
   - Go to Admin Panel
   - Find user with screens
   - Click "Unbind Screens"
   - Confirm action
   - Verify screens moved to unassigned controllers

3. **Test Password Reset**:
   - Click "Reset Password" for a user
   - Enter new password
   - Confirm action
   - Test login with new password

4. **Test User Deletion**:
   - Click "Delete" for a test user
   - Confirm deletion
   - Verify user removed from list
   - Verify screens moved to unassigned

### Testing Admin Redirect

1. **Login as Regular User**:
   - Should go to Dashboard

2. **Login as Admin User**:
   - Should go directly to Admin Panel

## 🚨 Security Considerations

### 2FA Security
- TOTP tokens expire after 30 seconds
- No token reuse allowed
- Secure secret storage in database
- Time-based validation prevents replay attacks

### Admin Function Security
- All admin endpoints require authentication
- Role-based access control enforced
- Super admin protection (cannot be modified/deleted)
- Audit trail in success/error messages

### Data Protection
- Screen unbinding preserves data
- User deletion moves screens to safe state
- No data loss during transitions
- Reversible operations where possible

## 📊 Migration Impact

### Database Changes
- **No schema changes required**
- Existing 2FA functionality enhanced
- All data preserved during update

### API Changes
- **Backward Compatible**: Existing API calls work unchanged
- **New Endpoints**: Additional admin endpoints added
- **Enhanced Responses**: Login endpoint enhanced with 2FA flow

### Frontend Changes
- **Progressive Enhancement**: Works with existing accounts
- **Responsive Design**: New UI elements follow existing patterns
- **Error Handling**: Comprehensive error states and messaging

## 🔧 Configuration

### Environment Variables
No new environment variables required. All features use existing configuration.

### Feature Flags
All features are enabled by default. To disable specific features:

```python
# In backend/app.py, you can comment out specific routes if needed
# @app.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
```

## 📈 Performance Impact

### 2FA Login Flow
- **Minimal Impact**: One additional database query for 2FA check
- **Caching**: User data fetched once per login
- **Network**: One additional API round-trip for 2FA users only

### Admin Functions
- **Database Operations**: Transactional for data consistency
- **UI Updates**: Auto-refresh after actions
- **Memory**: No significant memory overhead

## 🆘 Troubleshooting

### 2FA Not Working
1. **Check Time Sync**: Ensure server and device clocks are synchronized
2. **Verify Secret**: Check if 2FA secret is properly stored in database
3. **Token Format**: Ensure 6-digit numeric token format
4. **App Compatibility**: Verify authenticator app supports TOTP

### Admin Functions Failing
1. **Check Permissions**: Verify user has admin or administrator role
2. **Database Errors**: Check database connection and permissions
3. **Foreign Keys**: Ensure database foreign key constraints are working
4. **Session**: Verify admin session is valid and not expired

### Update Issues
1. **Git Conflicts**: Resolve any local changes before pulling
2. **Service Restart**: Ensure services restart properly after update
3. **Database Backup**: Verify backup creation before update
4. **Version Check**: Confirm version endpoint shows 1.2.0

## 📞 Support

### Getting Help
- **Version Info**: `curl http://localhost:5000/api/version`
- **Service Status**: `systemctl status lxcloud-backend nginx`
- **Logs**: `journalctl -u lxcloud-backend -f`
- **Database**: `mysql -u lxcloud -plxcloud123 lxcloud`

### Common Commands
```bash
# Check current version
curl http://localhost:5000/api/version

# Restart services
sudo systemctl restart lxcloud-backend nginx

# View recent logs
journalctl -u lxcloud-backend --since "10 minutes ago"

# Backup database manually
mysqldump -u lxcloud -plxcloud123 lxcloud > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 🎉 Summary

LXCloud v1.2.0 delivers significant improvements to admin functionality and security:

✅ **2FA Login Flow**: Enhanced security with seamless user experience
✅ **Admin Auto-Redirect**: Improved workflow for administrative users  
✅ **Screen Management**: Full control over user screen assignments
✅ **User Management**: Complete admin tools for password and account management
✅ **Update Ready**: Easy update path preserving all existing data

These features address all the requirements from the original request while maintaining backward compatibility and data integrity.