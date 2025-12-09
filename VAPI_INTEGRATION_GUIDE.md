# VAPI Voice Assistant Integration Guide

## Overview

This document describes the integration of VAPI AI voice assistant into the Chatbot Evaluation Platform, including the problems encountered and their solutions.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Problems & Solutions](#problems--solutions)
4. [Final Architecture](#final-architecture)
5. [Usage](#usage)

---

## Requirements

### VAPI Credentials

You need the following from your [VAPI Dashboard](https://dashboard.vapi.ai):

| Credential | Description | Location in Dashboard |
|------------|-------------|----------------------|
| **Public Key** | Used for browser/web SDK calls | Settings → API Keys → Public Key |
| **Assistant ID** | Unique ID of your voice assistant | Assistants → Select Assistant → Copy ID |

### Dependencies

```
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## Setup

### 1. Create `.env` File

```env
# VAPI Configuration
VAPI_PUBLIC_KEY=your_public_key_here
VAPI_ASSISTANT_ID=your_assistant_id_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Services

```bash
# Terminal 1: Start Streamlit app
streamlit run app.py

# Terminal 2: Start HTTP server for voice calls
python -m http.server 8080
```

### 4. Access the Application

- **Main App**: http://localhost:8501
- **Voice Call Page**: http://localhost:8080/vapi_call.html

---

## Problems & Solutions

### Problem 1: VAPI SDK Not Loading

**Error:**
```
Uncaught ReferenceError: exports is not defined
Uncaught ReferenceError: Vapi is not defined
```

**Cause:**
The VAPI Web SDK from CDN (`@vapi-ai/web`) is an ES module that cannot be loaded with a regular `<script>` tag.

**Solution:**
Use ES module import with `type="module"`:

```html
<script type="module">
    const VapiModule = await import('https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/+esm');
    const Vapi = VapiModule.default.default;  // Double-nested export
</script>
```

---

### Problem 2: "Vapi is not a constructor"

**Error:**
```
Uncaught TypeError: Vapi is not a constructor
```

**Cause:**
The VAPI module exports are double-nested (`module.default.default`).

**Solution:**
Access the constructor correctly:

```javascript
const VapiModule = await import('https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/+esm');
const Vapi = VapiModule.default.default;  // Access nested default
const vapi = new Vapi(publicKey);
```

---

### Problem 3: Call Stuck on "Connecting..."

**Error:**
```
Vapi error: [object Object]
```

**Cause:**
Streamlit's `st.components.v1.html()` creates an iframe with sandbox restrictions that block:
- WebRTC connections
- Microphone access (getUserMedia)

**Solution:**
Use the **official VAPI widget** instead of custom SDK integration:

```html
<script src="https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js"></script>
<vapi-widget
    public-key="your-public-key"
    assistant-id="your-assistant-id"
    mode="voice"
    size="full"
></vapi-widget>
```

---

### Problem 4: WebRTC Blocked in Iframe

**Error:**
```
Devices Error (Permission Denied): NotAllowedError: Permission denied
```

**Cause:**
Even with `allow="microphone"` attribute, Streamlit's nested iframes block WebRTC.

**Solution:**
Create a **standalone HTML page** served directly (not through Streamlit iframe):

```bash
# Serve the voice call page directly
python -m http.server 8080
```

Access at: `http://localhost:8080/vapi_call.html`

---

### Problem 5: Microphone Permission Denied on HTTP

**Error:**
```
NotAllowedError: Permission denied
```

**Cause:**
Some browsers require HTTPS for microphone access, or the user hasn't granted permission.

**Solutions:**

#### Option A: Grant Permission in Browser
1. Click the 🔒 icon in address bar
2. Go to "Site settings"
3. Set "Microphone" to "Allow"
4. Refresh the page

#### Option B: Add Site to Chrome Settings
1. Go to `chrome://settings/content/microphone`
2. Click "Add" under "Allowed to use your microphone"
3. Add `http://localhost:8080`

#### Option C: Use Chrome Flag
```bash
chrome.exe --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
```

#### Option D: Check Windows Microphone Settings
1. Windows Settings → Privacy & Security → Microphone
2. Enable "Microphone access"
3. Enable "Let apps access your microphone"
4. Ensure browser has permission

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Streamlit App     │    │   Voice Call Page           │ │
│  │   (port 8501)       │    │   (port 8080)               │ │
│  │                     │    │                             │ │
│  │  - Bot Selection    │───▶│  - VAPI Widget              │ │
│  │  - Call Button      │    │  - Microphone Access        │ │
│  │  - Feedback Form    │    │  - Live Conversation        │ │
│  │                     │    │                             │ │
│  └─────────────────────┘    └──────────────┬──────────────┘ │
│                                            │                 │
└────────────────────────────────────────────┼─────────────────┘
                                             │
                                             ▼
                               ┌─────────────────────────────┐
                               │        VAPI Cloud           │
                               │                             │
                               │  - Voice Processing         │
                               │  - AI Assistant             │
                               │  - Speech-to-Text           │
                               │  - Text-to-Speech           │
                               │                             │
                               └─────────────────────────────┘
```

---

## Usage

### Starting a Voice Call

1. Open the Streamlit app: `http://localhost:8501`
2. Click "📞 Call" on any bot card
3. Click "📞 Start Voice Call" button
4. A new tab opens with the voice call interface
5. Click "Talk with AI" button
6. Allow microphone access when prompted
7. Start speaking - the AI will respond!

### Direct Voice Call Access

Go directly to: `http://localhost:8080/vapi_call.html`

---

## Files Structure

```
Evaluation_Cycle/
├── app.py                    # Main Streamlit application
├── vapi_call.html            # Standalone voice call page
├── .env                      # VAPI credentials (not in git)
├── requirements.txt          # Python dependencies
└── VAPI_INTEGRATION_GUIDE.md # This documentation
```

---

## Troubleshooting

### Call not connecting?
1. Check browser console for errors (F12 → Console)
2. Verify VAPI credentials in `.env`
3. Ensure HTTP server is running on port 8080

### Can't hear the assistant?
1. Check speaker/headphone volume
2. Verify audio output device in system settings

### Assistant can't hear you?
1. Check microphone permissions in browser
2. Verify microphone is working in Windows settings
3. Try a different browser (Edge, Firefox)

### Widget not appearing?
1. Check if VAPI widget script loaded (Network tab)
2. Verify public key and assistant ID are correct
3. Clear browser cache and refresh

---

## Key Learnings

1. **VAPI Web SDK** requires ES module imports with proper nesting
2. **Streamlit iframes** block WebRTC - use standalone pages for voice
3. **Microphone access** on HTTP requires explicit browser permissions
4. **Official VAPI widget** is more reliable than custom SDK integration
5. **Localhost** is treated as secure origin by most browsers

---

## References

- [VAPI Documentation](https://docs.vapi.ai/)
- [VAPI Dashboard](https://dashboard.vapi.ai/)
- [VAPI Widget Integration](https://docs.vapi.ai/clients/web)
- [Streamlit Components](https://docs.streamlit.io/library/components)

---

*Last Updated: December 9, 2025*

