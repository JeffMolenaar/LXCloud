# Android Example for LXCloud Integration

This directory contains example code for integrating Android devices with the LXCloud platform.

## Quick Integration

Your Android app needs to send POST requests to the LXCloud server with screen information.

### Endpoint
```
POST http://your-lxcloud-server/api/device/update
Content-Type: application/json
```

### JSON Payload
```json
{
  "serial_number": "SCREEN001",
  "latitude": 52.3676,
  "longitude": 4.9041,
  "information": "Screen is displaying content normally"
}
```

### Example HTTP Request (Java/Kotlin)

```java
// Using OkHttp (add to build.gradle: implementation 'com.squareup.okhttp3:okhttp:4.9.3')
import okhttp3.*;
import org.json.JSONObject;

public class LXCloudClient {
    private static final String SERVER_URL = "http://your-server-ip";
    private final OkHttpClient client = new OkHttpClient();
    
    public void sendUpdate(String serialNumber, double latitude, double longitude, String info) {
        try {
            JSONObject json = new JSONObject();
            json.put("serial_number", serialNumber);
            json.put("latitude", latitude);
            json.put("longitude", longitude);
            json.put("information", info);
            
            RequestBody body = RequestBody.create(
                json.toString(),
                MediaType.parse("application/json")
            );
            
            Request request = new Request.Builder()
                .url(SERVER_URL + "/api/device/update")
                .post(body)
                .build();
            
            Response response = client.newCall(request).execute();
            if (response.isSuccessful()) {
                Log.d("LXCloud", "Update sent successfully");
            } else {
                Log.e("LXCloud", "Update failed: " + response.code());
            }
        } catch (Exception e) {
            Log.e("LXCloud", "Error sending update", e);
        }
    }
}
```

### Example Usage

```java
// In your main activity or service
LXCloudClient client = new LXCloudClient();

// Get device location (you'll need location permissions)
LocationManager locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
Location location = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);

if (location != null) {
    client.sendUpdate(
        "SCREEN001",  // Your device's serial number
        location.getLatitude(),
        location.getLongitude(),
        "Device is online and displaying content"
    );
}
```

### Required Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

### Periodic Updates

Set up a periodic task to send updates every few minutes:

```java
// Using AlarmManager for periodic updates
public class UpdateService extends Service {
    private static final int UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        sendPeriodicUpdate();
        return START_STICKY;
    }
    
    private void sendPeriodicUpdate() {
        // Get current location and send update
        LXCloudClient client = new LXCloudClient();
        // ... location logic ...
        client.sendUpdate(serialNumber, lat, lng, status);
        
        // Schedule next update
        Handler handler = new Handler();
        handler.postDelayed(this::sendPeriodicUpdate, UPDATE_INTERVAL);
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
```

### Error Handling

Always implement proper error handling:

```java
public void sendUpdateWithRetry(String serial, double lat, double lng, String info) {
    int maxRetries = 3;
    int retryCount = 0;
    
    while (retryCount < maxRetries) {
        try {
            sendUpdate(serial, lat, lng, info);
            break; // Success, exit loop
        } catch (Exception e) {
            retryCount++;
            Log.w("LXCloud", "Retry " + retryCount + " failed", e);
            if (retryCount < maxRetries) {
                try {
                    Thread.sleep(1000 * retryCount); // Exponential backoff
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }
}
```

### Configuration

Create a configuration class for your settings:

```java
public class LXCloudConfig {
    public static final String SERVER_URL = "http://your-server-ip";
    public static final String DEVICE_SERIAL = "SCREEN001"; // Get from device settings
    public static final int UPDATE_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
    public static final int MAX_RETRIES = 3;
}
```

### Testing

Test your integration:

1. Make sure your LXCloud server is running and accessible
2. Add your device serial number in the LXCloud web interface
3. Run your Android app and check the dashboard for updates
4. Monitor logs for any connection issues

### Security Considerations

For production use:

1. Use HTTPS instead of HTTP
2. Implement authentication if needed
3. Validate SSL certificates
4. Consider using device certificates for authentication

### Troubleshooting

Common issues:

1. **Network connectivity**: Ensure device has internet access
2. **Server unreachable**: Check firewall settings and server status
3. **Serial number mismatch**: Ensure serial number matches what's registered in LXCloud
4. **Location permissions**: Make sure location permissions are granted
5. **Background restrictions**: Handle Android's background execution limits

For more details, check the main LXCloud documentation.