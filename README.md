# Chatbot Evaluation Platform

A Streamlit-based frontend for testing and evaluating chatbots with integrated VAPI voice calling.

## Features

- 🤖 **Multiple Chatbot Interfaces**: Test different chatbots (Healthcare simulations)
- 💬 **Chat Mode**: Text-based conversations
- 📞 **Voice Call Mode**: Real-time voice calls with VAPI integration
- 📝 **Live Transcript**: See real-time transcription during voice calls
- 💾 **Export Chat**: Download chat history as JSON
- 📝 **Feedback System**: Rate messages and sessions
- 🎨 **Modern Dark UI**: Clean and intuitive interface

## Quick Start

### 1. Setup Environment

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Or create new venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure VAPI Credentials

Create a `.env` file in the project root:

```env
VAPI_PUBLIC_KEY=your_vapi_public_key_here
VAPI_ASSISTANT_ID=your_vapi_assistant_id_here
VAPI_API_KEY=your_vapi_api_key_here
```

Get your credentials from [Vapi.ai Dashboard](https://dashboard.vapi.ai):
- **Public Key**: Found in Account Settings
- **Assistant ID**: Found when you create/view an Assistant
- **API Key**: Found in Account Settings (for backend calls)

### 3. Run the App

```bash
streamlit run app.py
```

That's it! The app will:
- Start on `http://localhost:8501`
- Auto-start an HTTP server on port 8080 for voice calls
- Everything works with just **one command**

## Voice Call Feature

The voice call feature uses VAPI's Web SDK for real-time voice conversations:

### How It Works

1. Click **📞 Call** on any chatbot card
2. The voice call interface loads (embedded from `vapi_call.html`)
3. Click the **green call button** 📞 to start
4. **Allow microphone access** when prompted
5. Start speaking - the AI will respond in real-time!
6. View the **live transcript** on the right side
7. Click the **red button** 📴 to end the call

### Technical Details

- Voice calls use VAPI's WebRTC-based real-time communication
- The `vapi_call.html` file contains the full voice interface
- An HTTP server auto-starts on port 8080 to serve the voice page
- This bypasses iframe microphone restrictions in Streamlit

## Project Structure

```
.
├── app.py                    # Main Streamlit application
├── vapi_call.html           # Voice call interface (served on port 8080)
├── requirements.txt         # Python dependencies
├── .env                     # VAPI credentials (create this)
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── static/                  # Static files folder
└── README.md               # This file
```

## Configuration Files

### `.env` (Required for voice calls)
```env
VAPI_PUBLIC_KEY=96e66c5a-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VAPI_ASSISTANT_ID=b0bf28dc-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VAPI_API_KEY=your_private_api_key
```

### `.streamlit/config.toml` (Theme)
```toml
[server]
enableStaticServing = true

[theme]
primaryColor = "#4a9eff"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#1e2130"
textColor = "#fafafa"
font = "sans serif"
```

## Troubleshooting

### Voice Call Not Working

1. **Check microphone permissions**: Click the 🔒 icon in the browser address bar → Allow Microphone

2. **Check VAPI credentials**: Ensure `.env` file has correct keys

3. **Port 8080 in use**: The app auto-starts HTTP server on 8080. If blocked:
   ```powershell
   # Find and kill process on port 8080
   netstat -ano | findstr :8080
   taskkill /PID <PID> /F
   ```

4. **Browser compatibility**: Works best in Chrome/Edge. Firefox may require additional permissions.

### Call Connects But No Audio

- Ensure VAPI Assistant is properly configured with a voice provider
- Check VAPI dashboard for any errors in call logs
- Verify microphone is not muted in system settings

## Dependencies

```
streamlit
python-dotenv
requests
```

## VAPI Integration Notes

- **Public Key**: Used in frontend (vapi_call.html) to initialize VAPI SDK
- **Assistant ID**: Identifies which AI assistant handles the conversation
- **API Key**: Used for backend operations (optional for basic usage)

The voice interface (`vapi_call.html`) uses VAPI's ES Module SDK:
```javascript
import Vapi from 'https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/+esm';
const vapi = new Vapi(PUBLIC_KEY);
await vapi.start(ASSISTANT_ID);
```

## License

MIT License
