# Debug Logging for VAPI Calls

This document describes the debug logging features added to troubleshoot VAPI call errors.

## Overview

A comprehensive debug logging system was added to all VAPI call widgets to help identify and diagnose errors that occur during voice calls, especially during the call initiation phase.

## Files Modified

- `vapi_call.html` (+ `static/vapi_call.html`)
- `vapi_call_widget.html` (+ `vapi-static/vapi_call_widget.html`)
- `vapi_combined_widget.html` (+ `vapi-static/vapi_combined_widget.html`)

## Features Added

### 1. Debug Panel UI

A toggleable debug panel was added to each widget:

- **Toggle Button**: 🔧 icon in the corner to show/hide the debug panel
- **Clear Button**: 🗑️ to clear all logs
- **Copy Button**: 📋 to copy all logs to clipboard for sharing
- **Close Button**: ✕ to hide the panel

### 2. Color-Coded Log Entries

Logs are color-coded for easy identification:

| Type | Color | Usage |
|------|-------|-------|
| `info` | Blue | Normal operations, progress updates |
| `warn` | Orange | Warnings, non-critical issues |
| `error` | Red | Errors, failures |

### 3. Enhanced `startCall()` Function

The call initiation process now logs detailed step-by-step progress:

```
=== STARTING CALL ===
Environment: {assistantId: "...", online: true}
Step 1/3: Requesting microphone...
Microphone granted: {tracks: [{label: "...", readyState: "live"}]}
Step 2/3: Initiating VAPI connection...
Step 3/3: Call initiated {duration: "1234ms"}
```

### 4. Pre-flight Checks

Before starting a call, the system checks:

- **Network connectivity**: Detects if the user is offline
- **Microphone availability**: Verifies microphone access and status

### 5. Timeout Protection

- 30-second timeout on `vapi.start()` to prevent hanging forever
- Logs connection duration for performance analysis

### 6. Specific Error Messages

Instead of generic "An error occurred", users now see specific messages:

| Error Condition | User Message |
|-----------------|--------------|
| No internet | "No internet connection" |
| Microphone denied | "Microphone access denied" |
| No microphone found | "No microphone found" |
| Microphone busy | "Microphone in use" |
| Connection timeout | "Connection timeout" |
| 401 Unauthorized | "Auth failed - check API key" |
| 403 Forbidden | "Access denied" |
| 404 Not Found | "Assistant not found" |
| 429 Rate Limit | "Rate limit exceeded" |
| 500 Server Error | "Server error" |

### 7. Detailed Error Logging

When errors occur, the debug panel captures:

- Error message
- Error name/type
- Error code (if available)
- HTTP status (if available)
- Stack trace (partial, for debugging)
- Connection duration
- All additional error properties

## How to Use

1. **Open the debug panel**: Click the 🔧 button in the corner
2. **Reproduce the error**: Start a call and let the error occur
3. **Review logs**: Check the debug panel for detailed error information
4. **Copy logs**: Click 📋 to copy all logs to clipboard
5. **Share for support**: Paste the logs when reporting issues

## Code Structure

### Debug Functions

```javascript
// Log a message with optional data
debugLog(message, type, data)
// type: 'info' | 'warn' | 'error'

// Extract detailed error information
extractErrorDetails(error)
// Returns: { message, name, code, status, ...additionalProps }

// UI controls
toggleDebugPanel()  // Show/hide panel
clearDebugLogs()    // Clear all logs
copyDebugLogs()     // Copy to clipboard
```

### Log Entry Format

Each log entry contains:
- `timestamp`: ISO timestamp
- `type`: Log level (info/warn/error)
- `message`: Human-readable message
- `data`: Optional structured data object

## Console Logging

All debug logs are also written to the browser console for developers who prefer using browser DevTools. The appropriate console method is used based on log type:
- `console.log()` for info
- `console.warn()` for warnings
- `console.error()` for errors

## Troubleshooting Common Issues

### "VAPI not initialized"
- The VAPI SDK failed to load
- Check network connection
- Check browser console for SDK loading errors

### "Microphone access denied"
- User denied microphone permission
- Check browser settings for microphone permissions
- Try resetting site permissions

### "Connection timeout"
- Call took longer than 30 seconds to connect
- Check internet connection stability
- VAPI servers may be experiencing issues

### "Auth failed - check API key"
- Invalid or expired VAPI public key
- Verify PUBLIC_KEY in the code matches your VAPI account

### "Assistant not found"
- Invalid ASSISTANT_ID
- Verify the assistant exists in your VAPI dashboard
