# Chatbot Evaluation Platform

A Streamlit-based frontend for testing and evaluating 6 different chatbots, similar to Dify's interface.

## Features

- 🤖 **6 Chatbot Interfaces**: Test up to 6 different chatbots simultaneously
- 💬 **Chat & 📞 Call Modes**: Switch between text chat and voice call modes for each bot
- 🎤 **Vapi Integration**: Frontend integration with Vapi for voice AI conversations
- ⚙️ **Bot Configuration**: Configure Vapi API keys and Assistant IDs for each bot
- 📊 **Statistics**: View message counts and chat statistics
- 💾 **Export Chat**: Download chat history as JSON
- 📝 **Feedback System**: Rate individual messages and overall sessions
- 🎨 **Modern UI**: Clean and intuitive interface

## Installation

1. Create and activate virtual environment:

   **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   **Windows (Command Prompt):**
   ```cmd
   venv\Scripts\activate.bat
   ```

   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your browser at `http://localhost:8501`

3. Select a bot from the sidebar to start chatting

4. Configure Vapi in the "Bot Settings - Vapi" section:
   - Enable Vapi for the bot
   - Enter your Vapi API Key
   - Enter the Assistant ID
   - (Optional) Enter Phone Number ID for call mode

5. Switch between Chat and Call modes using the radio buttons in the sidebar

## Vapi Integration

This platform uses **Vapi's frontend JavaScript SDK** for voice AI conversations. Vapi handles both chat and call modes directly in the browser.

### Setting Up Vapi

1. **Get Vapi Credentials**:
   - Sign up at [Vapi.ai](https://vapi.ai)
   - Create an Assistant in your Vapi dashboard
   - Get your API Key and Assistant ID

2. **Configure in App**:
   - Go to "Bot Settings - Vapi" in the sidebar
   - Enable Vapi for the bot
   - Enter your Vapi API Key
   - Enter the Assistant ID
   - Save the configuration

3. **Use Vapi Widget**:
   - Once configured, the Vapi widget will appear in the main area
   - For Chat mode: Use the Vapi chat widget
   - For Call mode: Use the Vapi phone call widget
   - All interactions are handled by Vapi's frontend SDK

### Vapi Features

- **Chat Mode**: Text-based conversations via Vapi chat widget
- **Call Mode**: Voice conversations via Vapi phone call widget
- **Real-time**: All interactions happen in real-time through Vapi's infrastructure
- **No Backend Required**: Vapi handles all API calls and audio processing

## Backend Integration (Fallback)

If Vapi is not configured, the app falls back to Streamlit's native chat interface. To connect to your own backend, modify the `send_message()` function in `app.py`:

```python
def send_message(bot_name: str, user_message: str):
    """Send message to chatbot"""
    # Add user message to history
    st.session_state.bots[bot_name]['messages'].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Get API config for this bot
    api_config = st.session_state.api_configs[bot_name]
    
    # Make API call to your backend
    import requests
    response = requests.post(
        api_config['url'],
        json={'message': user_message},
        headers={
            'Authorization': f"Bearer {api_config['api_key']}",
            **api_config['headers']
        }
    )
    
    bot_response = response.json()['response']  # Adjust based on your API
    
    # Add bot response to history
    st.session_state.bots[bot_name]['messages'].append({
        'role': 'assistant',
        'content': bot_response,
        'timestamp': datetime.now().isoformat()
    })
```

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore file
└── venv/              # Virtual environment (created after setup)
```

## Customization

- **Bot Names**: Edit the `bots` dictionary in `app.py` to change bot names and descriptions
- **Styling**: Modify the CSS in the `st.markdown()` section for custom styling
- **API Integration**: Update `send_message()` function to connect to your backend

