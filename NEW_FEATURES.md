# LXCloud New Features - Admin System & Controller Management

This document describes the new features added to LXCloud for admin functionality and improved controller management.

## New Features Overview

### 1. Controller Self-Registration
Controllers can now register themselves with the LXCloud system without requiring manual setup.

**Endpoint:** `POST /api/controller/register`
```json
{
  "serial_number": "CTRL_001",
  "latitude": 52.3676,
  "longitude": 4.9041
}
```

**Key Benefits:**
- Controllers automatically appear in the system when they come online
- Unassigned controllers are visible to admins but don't store data
- Users can assign controllers by entering just the serial number

### 2. Admin System
Two-tier administration system with comprehensive user and controller management.

#### Super Admin
- Full system access
- Can promote users to administrator status
- Can view all screens and unassigned controllers
- Created using special admin key

#### Administrator
- Can view all screens and unassigned controllers
- Can manage most system aspects
- Promoted by super admin

**Admin Creation:**
```bash
curl -X POST http://localhost:5000/api/admin/create-admin \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com", 
    "password": "securepassword",
    "admin_key": "lxcloud-admin-setup-2024"
  }'
```

### 3. User Security Features

#### Password Management
- Secure password change functionality
- Current password verification required

#### Two-Factor Authentication (2FA)
- QR code setup with authenticator apps
- TOTP-based verification
- Enable/disable functionality

#### User Profile Management
- Profile information display
- Security settings access
- Admin status indicators

### 4. Enhanced Data Security

#### Data Isolation
- Unassigned controllers don't store sensor data
- Data only saved when controller is assigned to a user
- Prevents data leakage between users

#### Assignment Protection
- Controllers can only be assigned to one user
- Prevents duplicate assignments
- Clear assignment status tracking

## API Endpoints Reference

### Admin Endpoints
```
GET    /api/admin/users                    - List all users (admin only)
POST   /api/admin/users/{id}/toggle-admin  - Toggle user admin status
POST   /api/admin/create-admin             - Create initial admin account
```

### User Management
```
POST   /api/user/change-password           - Change user password
POST   /api/user/2fa/setup                 - Setup 2FA
POST   /api/user/2fa/verify                - Verify and enable 2FA
POST   /api/user/2fa/disable               - Disable 2FA
```

### Controller Management
```
POST   /api/controller/register            - Controller self-registration
GET    /api/screens                        - Get screens (enhanced for admins)
```

## Frontend Features

### User Interface
- **Header Dropdown:** User menu with profile options
- **Profile Page:** Account information and security settings
- **Password Change:** Secure password update form
- **2FA Management:** Setup and manage two-factor authentication
- **Admin Panel:** Comprehensive admin dashboard

### Admin Dashboard
- User management with role assignment
- Screen overview with assignment status
- Unassigned controller monitoring
- System statistics and metrics

## Usage Examples

### 1. Controller Setup
```python
import requests

# Controller registers itself
response = requests.post('http://localhost:5000/api/controller/register', json={
    'serial_number': 'CTRL_001',
    'latitude': 52.3676,
    'longitude': 4.9041
})
```

### 2. User Assigns Controller
```javascript
// User adds screen by serial number
api.addScreen({
  serial_number: 'CTRL_001',
  custom_name: 'Office Display'
})
```

### 3. Admin Views All Controllers
Admins can see both assigned screens and unassigned controllers in the admin panel.

## Security Considerations

### Controller Registration
- Registration endpoint is public but logged
- Controllers identified by unique serial numbers
- Location data validated and sanitized

### Admin Access
- Admin creation requires special key
- Role-based access control throughout system
- Session-based authentication maintained

### Data Protection
- 2FA protects against account compromise
- Password changes require current password
- Data isolation prevents cross-user access

## Testing

### Run Feature Tests
```bash
./test_new_features.py
```

### Demo Controller Simulation
```bash
./demo_controller.py
```

## Migration Notes

### Database Changes
The new features require database schema updates. These are automatically applied when the backend starts:

- `users` table: Added `is_admin`, `is_administrator`, `two_fa_enabled`, `two_fa_secret`
- `controllers` table: New table for unassigned controller registration
- `screens` table: Enhanced with assignment tracking

### Backwards Compatibility
- Existing screens continue to work unchanged
- Current user accounts maintain full functionality
- API endpoints remain compatible

## Configuration

### Environment Variables
```bash
# Default admin key (change in production)
ADMIN_KEY=your-secure-admin-key-here
```

### Production Recommendations
1. Change the default admin key
2. Enable HTTPS for 2FA QR codes
3. Configure proper email for account notifications
4. Set up database backups for controller data
5. Monitor unassigned controller activity

## Troubleshooting

### Common Issues
1. **Controllers not appearing:** Check registration endpoint connectivity
2. **Admin creation fails:** Verify admin key is correct
3. **2FA setup fails:** Ensure proper time synchronization
4. **Assignment fails:** Check if controller is already assigned

### Debug Mode
Enable debug logging in the backend for detailed troubleshooting:
```python
app.run(debug=True)
```