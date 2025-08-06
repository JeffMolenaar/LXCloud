# Controller Workflow Documentation

This document explains the complete controller registration and assignment workflow in LXCloud.

## Overview

LXCloud implements a secure controller management system where:

1. **Controllers register independently** via API with authentication
2. **Controllers remain unassigned** until explicitly assigned by users
3. **Data is only stored** when controllers are assigned to users
4. **Admin can see all controllers** (assigned and unassigned)
5. **Users can only assign available controllers** by serial number

## Workflow Steps

### 1. Controller Registration

Controllers (LED screens with Android devices) register themselves with the system:

```bash
# Calculate authentication key
SERIAL="SCREEN001"
AUTH_KEY=$(echo -n "lxcloud-controller-$SERIAL" | sha256sum | cut -c1-16)

# Register with LXCloud
curl -X POST http://your-server:5000/api/controller/register \
  -H 'Content-Type: application/json' \
  -d '{
    "serial_number": "'$SERIAL'",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "auth_key": "'$AUTH_KEY'"
  }'
```

**What happens:**
- Controller is added to `controllers` table
- Status is set to `assigned = FALSE`
- Registration key is generated for the controller
- Controller appears in admin panel as "unassigned"

### 2. Controller Operation (Unassigned)

While unassigned, controllers continue to operate and send updates:

```bash
curl -X POST http://your-server:5000/api/device/update \
  -H 'Content-Type: application/json' \
  -d '{
    "serial_number": "SCREEN001",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "information": "Status update"
  }'
```

**What happens:**
- Location and status are updated in `controllers` table
- **No data is stored** in `screen_data` table
- Controller remains visible to admin only

### 3. User Assignment

Users assign controllers by entering the serial number:

```bash
# User must be logged in (session-based)
curl -X POST http://your-server:5000/api/screens \
  -H 'Content-Type: application/json' \
  -H 'Cookie: session=user_session_cookie' \
  -d '{
    "serial_number": "SCREEN001",
    "custom_name": "Office Display"
  }'
```

**What happens:**
- Controller is moved from `controllers` to `screens` table
- `assigned = TRUE` is set in controllers table
- Screen is linked to the user (`user_id`)
- Controller now appears in user's dashboard

### 4. Controller Operation (Assigned)

After assignment, controllers store data:

```bash
curl -X POST http://your-server:5000/api/device/update \
  -H 'Content-Type: application/json' \
  -d '{
    "serial_number": "SCREEN001",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "information": "Now storing data!"
  }'
```

**What happens:**
- Location and status are updated in `screens` table
- **Data is stored** in `screen_data` table
- Real-time updates are sent to connected users
- Screen appears on user's map dashboard

## Admin Capabilities

### View All Controllers

Admin users can see both assigned and unassigned controllers:

```bash
curl -X GET http://your-server:5000/api/screens \
  -H 'Cookie: session=admin_session_cookie'
```

Response includes:
```json
{
  "screens": [
    {
      "id": 1,
      "serial_number": "SCREEN001",
      "assigned_user": "john_doe",
      "online_status": true,
      "assigned": true
    }
  ],
  "unassigned_controllers": [
    {
      "id": 2,
      "serial_number": "SCREEN002",
      "assigned_user": null,
      "online_status": true,
      "assigned": false,
      "is_controller": true
    }
  ]
}
```

### User Management

Admin can grant administrator privileges:

```bash
curl -X POST http://your-server:5000/api/admin/users/2/toggle-admin \
  -H 'Cookie: session=admin_session_cookie'
```

## Security Features

### Authentication Keys

Controllers use SHA256-based authentication:
```bash
# Generate auth key
AUTH_KEY=$(echo -n "lxcloud-controller-SERIAL_NUMBER" | sha256sum | cut -c1-16)
```

### Access Control

- **Super Admin (`is_admin = true`)**: Full system access, cannot be modified
- **Administrator (`is_administrator = true`)**: Can manage users and see all controllers
- **Regular Users**: Can only see and manage their assigned controllers

### Data Privacy

- Unassigned controllers: Location and status only, no data storage
- Assigned controllers: Full data collection and storage
- User isolation: Users can only access their own assigned controllers

## Database Flow

### Before Assignment
```
Controller Registration → controllers table → Admin visibility only
                                           ↓
Controller Updates → Update location/status → No data storage
```

### After Assignment
```
User Assignment → Move to screens table → User visibility
                                       ↓
Controller Updates → Update location/status → Store in screen_data
```

## Demo Script

Run the included demo to see the complete workflow:

```bash
cd LXCloud
python3 demo_controller_workflow.py
```

This demonstrates:
1. Controller registration
2. Admin viewing unassigned controllers
3. Controller assignment
4. Data storage behavior change
5. Real-time updates

## Troubleshooting

### Controller Not Appearing
- Check authentication key calculation
- Verify controller is sending correct serial number
- Check network connectivity to LXCloud server

### Assignment Fails
- Ensure controller is registered first
- Verify controller is not already assigned
- Check user has permission to assign controllers

### Data Not Storing
- Verify controller is assigned to a user
- Check `/api/device/update` endpoint is being used
- Confirm information field is provided in requests