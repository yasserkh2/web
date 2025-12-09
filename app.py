import streamlit as st
import json
import requests
import os
import threading
import http.server
import socketserver
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Start HTTP server for vapi_call.html in background (only once)
def start_http_server():
    """Start a simple HTTP server on port 8080 for serving vapi_call.html"""
    try:
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except OSError:
        pass  # Port already in use (server already running)

# Start server in background thread (check if not already started)
if 'http_server_started' not in st.session_state:
    st.session_state.http_server_started = True
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()

# VAPI Configuration from environment
VAPI_API_KEY = os.getenv('VAPI_API_KEY', '')
VAPI_PUBLIC_KEY = os.getenv('VAPI_PUBLIC_KEY', '')
VAPI_ASSISTANT_ID = os.getenv('VAPI_ASSISTANT_ID', '')

# Page configuration
st.set_page_config(
    page_title="Chatbot Evaluation Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Additional dark mode CSS for better visibility and PLATO-style UI
st.markdown("""
<style>
    /* Use the full browser width for the entire app */
    [data-testid="stAppViewContainer"] {
        max-width: 100% !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove Streamlit's default central column width */
    .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }

    /* Make the app fill the full viewport height */
    [data-testid="stAppViewContainer"] > .main {
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Allow block-container to grow */
    .block-container {
        flex: 1 !important;
    }

    /* Make columns align properly and prevent wrapping */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
        flex-wrap: nowrap !important;
        gap: 1rem !important;
    }
    
    /* Ensure columns don't shrink too much */
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        min-width: 0 !important;
    }

    /* Hide Streamlit header/deploy bar */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Hide main menu button */
    #MainMenu {
        display: none !important;
    }
    
    /* Hide footer */
    footer {
        display: none !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e2130 0%, #262730 100%) !important;
        border-right: 1px solid rgba(74, 158, 255, 0.2) !important;
        width: 150px !important;
        min-width: 150px !important;
    }
    
    [data-testid="stSidebarContent"] {
        padding: 0rem 0.5rem 0.5rem 0.5rem !important;
    }
    
    /* Hide collapse button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Style sidebar buttons */
    [data-testid="stSidebar"] button {
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        margin: 0.1rem 0 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: rgba(74, 158, 255, 0.2) !important;
    }
    
    [data-testid="stSidebar"] button[disabled] {
        background: rgba(74, 158, 255, 0.3) !important;
        opacity: 1 !important;
    }
    
    /* Ensure app takes full viewport */
    html, body {
        overflow-x: hidden !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove any leftover spacer/anchor elements */
    [data-testid="stAppIframeResizerAnchor"] {
        display: none !important;
        height: 0 !important;
    }
    
    /* Hide any floating Vapi widgets */
    .vapi-widget, [class*="vapi"], #vapi-widget {
        display: none !important;
    }
    
    /* Ensure text visibility in dark mode */
    .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {
        color: #fafafa;
    }
    
    label {
        color: #fafafa;
    }
    
    .stCaption {
        color: #b0b0b0;
    }
    
    .stChatMessage p {
        color: #fafafa;
    }
    
    /* PLATO-style Cards */
    /* Horizontal scrollable cards container */
    .plato-cards-container {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 1.5rem;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding: 1rem 0 1.5rem 0;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        width: 100%;
        align-items: stretch;
        white-space: nowrap;
    }
    
    /* Fixed size card wrapper */
    .plato-card-wrapper {
        flex: 0 0 280px !important;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        height: 420px;
        position: relative;
        display: inline-block;
        vertical-align: top;
        white-space: normal;
    }
    
    /* Card styling - fixed height for uniformity */
    .plato-card {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid rgba(74, 158, 255, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }
    
    .plato-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(74, 158, 255, 0.3);
        border-color: #4a9eff;
    }
    
    /* Card tag */
    .plato-card-tag {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background: rgba(74, 158, 255, 0.2);
        color: #4a9eff;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        width: fit-content;
    }
    
    /* Card avatar section */
    .plato-card-avatar-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 0.75rem;
    }
    
    .plato-card-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4a9eff 0%, #3a8eef 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        border: 3px solid #4a9eff;
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.4);
    }
    
    /* Card title */
    .plato-card-title {
        color: #fafafa;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0.5rem 0 0.25rem 0;
        text-align: center;
        line-height: 1.3;
    }
    
    /* Card name/subtitle */
    .plato-card-name {
        color: #b0b0b0;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Card description */
    .plato-card-description {
        color: #d0d0d0;
        font-size: 0.75rem;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.4;
        flex-grow: 1;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
    
    /* Button wrapper - push to bottom */
    .plato-card-button-wrapper {
        margin-top: auto;
        width: 100%;
        display: flex;
        gap: 0.5rem;
    }
    
    /* Card buttons */
    .plato-card-btn {
        flex: 1;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        text-align: center;
    }
    
    .plato-card-btn-primary {
        background: #4a9eff;
        color: #fafafa;
    }
    
    .plato-card-btn-primary:hover {
        background: #3a8eef;
        transform: scale(1.02);
    }
    
    .plato-card-btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: #fafafa;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .plato-card-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Scrollbar styling */
    .plato-cards-container::-webkit-scrollbar {
        height: 10px;
    }
    
    .plato-cards-container::-webkit-scrollbar-track {
        background: #1e2130;
        border-radius: 5px;
    }
    
    .plato-cards-container::-webkit-scrollbar-thumb {
        background: #4a9eff;
        border-radius: 5px;
    }
    
    /* Ensure Streamlit doesn't wrap the cards container */
    div[data-testid="stMarkdownContainer"]:has(.plato-cards-container) {
        overflow-x: visible !important;
        width: 100% !important;
    }
    
    div[data-testid="stMarkdownContainer"] .plato-cards-container {
        display: flex !important;
        flex-wrap: nowrap !important;
    }
    
    /* Welcome Section */
    .plato-welcome {
        margin-bottom: 2rem;
    }
    
    .plato-welcome-title {
        font-size: 3rem;
        font-weight: bold;
        color: #fafafa;
        margin-bottom: 0.5rem;
    }
    
    .plato-welcome-subtitle {
        font-size: 1.2rem;
        color: #b0b0b0;
        margin-bottom: 2rem;
    }
    
    /* Feedback Popup Modal */
    .feedback-popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.75);
        z-index: 9998;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .feedback-popup-content {
        background-color: #1e2130;
        border: 3px solid #4a9eff;
        border-radius: 15px;
        padding: 2.5rem;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 10px 50px rgba(0, 0, 0, 0.8);
        text-align: center;
        animation: popupSlideIn 0.3s ease-out;
    }
    
    @keyframes popupSlideIn {
        from {
            transform: translateY(-50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .feedback-popup-title {
        color: #fafafa;
        font-size: 1.8rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .feedback-popup-text {
        color: #fafafa;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .feedback-popup-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
    
    .feedback-popup-btn {
        flex: 1;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .feedback-popup-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .feedback-popup-btn-like {
        background-color: #4aff9e;
        color: #0e1117;
    }
    
    .feedback-popup-btn-dislike {
        background-color: #ff4a4a;
        color: #fafafa;
    }
    
</style>
<script>
function triggerCallButtonDirect(botName) {
    // Use query parameters to trigger the action
    const params = new URLSearchParams(window.location.search);
    params.set('bot', botName);
    params.set('action', 'call');
    window.location.search = params.toString();
}

function triggerProfileButton(botName) {
    // Use query parameters to trigger profile view
    const params = new URLSearchParams(window.location.search);
    params.set('bot', botName);
    params.set('action', 'profile');
    window.location.search = params.toString();
}
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'home'  # 'home' or 'bot_detail'

if 'bots' not in st.session_state:
    st.session_state.bots = {
        'Bot 1': {
            'name': 'Bot 1', 
            'display_name': 'Alzheimer Patient',
            'customer_segment': 'Healthcare Providers',
            'messages': []
        },
        'Bot 2': {
            'name': 'Bot 2', 
            'display_name': 'Sales Excellence Coach',
            'customer_segment': 'Sales Team',
            'messages': []
        },
        'Bot 3': {
            'name': 'Bot 3', 
            'display_name': 'Ibuprofen Knowledge Tester',
            'customer_segment': 'Medical Professionals',
            'messages': []
        },
        'Bot 4': {
            'name': 'Bot 4', 
            'display_name': 'Breast Cancer Oncologist',
            'customer_segment': 'Oncologists',
            'messages': []
        },
        'Bot 5': {
            'name': 'Bot 5', 
            'display_name': 'Herceptin Specialist',
            'customer_segment': 'Specialists',
            'messages': []
        },
        'Bot 6': {
            'name': 'Bot 6', 
            'display_name': 'Cardiology Expert',
            'customer_segment': 'Cardiologists',
            'messages': []
        },
    }

if 'selected_bot' not in st.session_state:
    st.session_state.selected_bot = 'Bot 1'

if 'api_configs' not in st.session_state:
    st.session_state.api_configs = {
        'Bot 1': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
        'Bot 2': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
        'Bot 3': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
        'Bot 4': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
        'Bot 5': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
        'Bot 6': {
            'vapi_api_key': '', 
            'assistant_id': '', 
            'phone_number_id': '',
            'server_url': 'https://api.vapi.ai',
            'use_vapi': False
        },
    }

if 'active_calls' not in st.session_state:
    st.session_state.active_calls = {}  # {bot_name: call_id}

if 'call_status' not in st.session_state:
    st.session_state.call_status = {}  # {bot_name: 'idle' | 'ringing' | 'active' | 'ended'}

if 'like_dislike_feedback' not in st.session_state:
    st.session_state.like_dislike_feedback = {}  # {bot_name: {message_index: 'like' | 'dislike' | None}}

if 'dislike_reasons' not in st.session_state:
    st.session_state.dislike_reasons = {}  # {bot_name: {message_index: 'reason text'}}

if 'dislike_popup_open' not in st.session_state:
    st.session_state.dislike_popup_open = {}  # {bot_name: message_index or None}

if 'call_overall_feedback' not in st.session_state:
    st.session_state.call_overall_feedback = {}  # {bot_name: 'like' | 'dislike' | None}

if 'show_feedback_popup' not in st.session_state:
    st.session_state.show_feedback_popup = {}  # {bot_name: True/False}

if 'feedback' not in st.session_state:
    st.session_state.feedback = {}  # {bot_name: {message_index: {rating, comment, timestamp}}}

if 'session_feedback' not in st.session_state:
    st.session_state.session_feedback = {}  # {bot_name: {rating, comment, timestamp}}

if 'feedback_form_open' not in st.session_state:
    st.session_state.feedback_form_open = None  # Track which message feedback form is open

if 'session_feedback_form_open' not in st.session_state:
    st.session_state.session_feedback_form_open = False  # Track if session feedback form is open

if 'bot_modes' not in st.session_state:
    st.session_state.bot_modes = {
        'Bot 1': 'chat',  # 'chat' or 'call'
        'Bot 2': 'chat',
        'Bot 3': 'chat',
        'Bot 4': 'chat',
        'Bot 5': 'chat',
        'Bot 6': 'chat',
    }

if 'call_messages' not in st.session_state:
    st.session_state.call_messages = {
        'Bot 1': [],
        'Bot 2': [],
        'Bot 3': [],
        'Bot 4': [],
        'Bot 5': [],
        'Bot 6': [],
    }

if 'vapi_call_id' not in st.session_state:
    st.session_state.vapi_call_id = {}  # {bot_name: call_id}

if 'live_transcript' not in st.session_state:
    st.session_state.live_transcript = {}  # {bot_name: [transcript_entries]}



def render_call_interface(bot_name: str):
    """Render call interface - embeds vapi_call.html from HTTP server"""
    bot_data = st.session_state.bots.get(bot_name, {})
    display_name = bot_data.get('display_name', bot_name)
    avatar_emoji = bot_data.get('avatar_emoji', '🤖')
    
    # Check if VAPI is configured
    has_vapi = VAPI_PUBLIC_KEY and VAPI_ASSISTANT_ID and VAPI_PUBLIC_KEY != 'your_vapi_public_key_here'
    
    if has_vapi:
        # Embed the vapi_call.html page via iframe from auto-started HTTP server
        st.components.v1.iframe(
            src="http://localhost:8080/vapi_call.html",
            height=700,
            scrolling=True
        )
        
        # Home button below the iframe
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True, key="back_home_call"):
                st.session_state.view_mode = 'home'
                st.rerun()
    else:
        # VAPI not configured - show setup instructions
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{avatar_emoji}</div>
                <h2 style="color: #fafafa;">{display_name}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.error("⚠️ VAPI not configured")
            st.markdown("""
            **To enable voice calls, add these to your `.env` file:**
            ```
            VAPI_PUBLIC_KEY=your_public_key
            VAPI_ASSISTANT_ID=your_assistant_id
            ```
            """)
            
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.view_mode = 'home'
                st.rerun()

def render_vapi_widget(bot_name: str, mode: str, assistant_id: str, api_key: str):
    """Render Vapi widget for chat or call mode"""
    if not assistant_id or not api_key:
        st.warning("⚠️ Please configure Vapi Assistant ID and API Key in Bot Settings")
        return
    
    widget_type = 'chat' if mode == 'chat' else 'phone-call'
    widget_id = f"vapi-widget-{bot_name}-{mode}"
    
    vapi_html = f"""
    <div id="{widget_id}"></div>
    <script src="https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest"></script>
    <script>
        (function() {{
            const widgetId = '{widget_id}';
            const assistantId = '{assistant_id}';
            const apiKey = '{api_key}';
            const mode = '{mode}';
            
            // Initialize Vapi
            if (typeof window.vapiWidgets === 'undefined') {{
                window.vapiWidgets = {{}};
            }}
            
            // Clean up existing widget if switching modes
            if (window.vapiWidgets[widgetId]) {{
                window.vapiWidgets[widgetId].destroy();
            }}
            
            // Create Vapi widget
            const config = {{
                assistantId: assistantId,
                apiKey: apiKey,
                type: mode === 'chat' ? 'chat' : 'phone-call',
                position: 'bottom-right',
                onMessage: function(message) {{
                    // Handle messages from Vapi
                    console.log('Vapi message:', message);
                    // Send message to Streamlit backend via custom event
                    window.parent.postMessage({{
                        type: 'vapi-message',
                        botName: '{bot_name}',
                        mode: mode,
                        message: message
                    }}, '*');
                }},
                onCallStart: function(call) {{
                    console.log('Call started:', call);
                    window.parent.postMessage({{
                        type: 'vapi-call-start',
                        botName: '{bot_name}',
                        callId: call.id
                    }}, '*');
                }},
                onCallEnd: function(call) {{
                    console.log('Call ended:', call);
                    window.parent.postMessage({{
                        type: 'vapi-call-end',
                        botName: '{bot_name}',
                        callId: call.id
                    }}, '*');
                }}
            }};
            
            if (mode === 'chat') {{
                window.vapiWidgets[widgetId] = new Vapi.ChatWidget(config);
            }} else {{
                window.vapiWidgets[widgetId] = new Vapi.PhoneCallWidget(config);
            }}
            
            // Render widget
            window.vapiWidgets[widgetId].render(document.getElementById(widgetId));
        }})();
    </script>
    """
    
    st.components.v1.html(vapi_html, height=600, scrolling=True)

def send_message(bot_name: str, user_message: str, mode: str = 'chat'):
    """Send message to chatbot - uses Vapi if configured, otherwise mock"""
    config = st.session_state.api_configs[bot_name]
    use_vapi = config.get('use_vapi', False) and config.get('assistant_id') and config.get('vapi_api_key')
    
    if mode == 'chat':
        # Add user message to history
        st.session_state.bots[bot_name]['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'mode': 'chat',
            'source': 'vapi' if use_vapi else 'mock'
        })
        
        if use_vapi:
            # Vapi handles the response via frontend widget
            # Message will be added when Vapi sends response
            pass
        else:
            # Mock response
            mock_response = f"This is a mock response from {bot_name}. Your message: '{user_message}'"
            st.session_state.bots[bot_name]['messages'].append({
                'role': 'assistant',
                'content': mock_response,
                'timestamp': datetime.now().isoformat(),
                'mode': 'chat',
                'source': 'mock'
            })
    else:  # call mode
        # For call mode, Vapi handles audio via frontend widget
        if not use_vapi:
            # Mock call response
            st.session_state.call_messages[bot_name].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat(),
                'mode': 'call',
                'source': 'mock'
            })
            
            mock_response = f"This is a mock voice response from {bot_name}. You said: '{user_message}'"
            st.session_state.call_messages[bot_name].append({
                'role': 'assistant',
                'content': mock_response,
                'timestamp': datetime.now().isoformat(),
                'mode': 'call',
                'source': 'mock'
            })

def send_audio_call(bot_name: str, audio_data):
    """Send audio to chatbot for call mode (will connect to backend later)"""
    # TODO: Replace with actual API call to backend
    # This would send audio to backend, get audio response back
    # For now, return mock response
    mock_transcription = "User audio transcription"
    mock_response = f"This is a mock voice response from {bot_name}."
    
    st.session_state.call_messages[bot_name].append({
        'role': 'user',
        'content': mock_transcription,
        'timestamp': datetime.now().isoformat(),
        'mode': 'call',
        'audio': audio_data  # Store audio data if needed
    })
    
    st.session_state.call_messages[bot_name].append({
        'role': 'assistant',
        'content': mock_response,
        'timestamp': datetime.now().isoformat(),
        'mode': 'call'
    })

def save_feedback(bot_name: str, message_index: int, rating: int, comment: str):
    """Save user feedback for a specific bot response"""
    if bot_name not in st.session_state.feedback:
        st.session_state.feedback[bot_name] = {}
    
    st.session_state.feedback[bot_name][message_index] = {
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat()
    }

def save_session_feedback(bot_name: str, rating: int, comment: str):
    """Save overall session feedback for a bot"""
    st.session_state.session_feedback[bot_name] = {
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat(),
        'message_count': len(st.session_state.bots[bot_name]['messages'])
    }

def reset_session_for_bot(bot_name: str):
    """Reset session for a bot - clear messages, feedback, and return to home state"""
    # Clear messages
    st.session_state.bots[bot_name]['messages'] = []
    st.session_state.call_messages[bot_name] = []
    
    # Reset call status
    st.session_state.call_status[bot_name] = 'idle'
    st.session_state.active_calls.pop(bot_name, None)
    
    # Clear feedback states
    st.session_state.feedback.pop(bot_name, None)
    st.session_state.like_dislike_feedback.pop(bot_name, None)
    st.session_state.dislike_reasons.pop(bot_name, None)
    st.session_state.dislike_popup_open.pop(bot_name, None)
    
    # Reset popup and feedback form states
    st.session_state.show_feedback_popup[bot_name] = False
    st.session_state.call_overall_feedback[bot_name] = None
    st.session_state.session_feedback_form_open = False
    st.session_state.feedback_form_open = None
    
    # Return to home page
    st.session_state.view_mode = 'home'

def save_like_dislike(bot_name: str, message_index: int, reaction: str, reason: str = None):
    """Save like/dislike feedback for a specific message"""
    if bot_name not in st.session_state.like_dislike_feedback:
        st.session_state.like_dislike_feedback[bot_name] = {}
    st.session_state.like_dislike_feedback[bot_name][message_index] = reaction
    
    # Save dislike reason if provided
    if reaction == 'dislike' and reason:
        if bot_name not in st.session_state.dislike_reasons:
            st.session_state.dislike_reasons[bot_name] = {}
        st.session_state.dislike_reasons[bot_name][message_index] = reason
    elif reaction != 'dislike':
        # Remove reason if not disliking
        if bot_name in st.session_state.dislike_reasons and message_index in st.session_state.dislike_reasons[bot_name]:
            del st.session_state.dislike_reasons[bot_name][message_index]

def display_call_transcript(bot_name: str):
    """Display call transcript with like/dislike buttons for each bot response"""
    messages = st.session_state.call_messages[bot_name]
    
    if not messages:
        # Show sample transcript for demonstration with interactive like/dislike
        st.info("💡 **Sample Call Transcript** - Click 👍 or 👎 to test the feedback functionality")
        
        # Add button to load sample messages for testing
        if st.button("📝 Load Sample Messages for Testing", use_container_width=True, type="primary"):
            sample_messages = [
                {'role': 'user', 'content': 'Hello, I need help with my account', 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': 'Hello! I\'d be happy to help you with your account. What specific issue are you experiencing?', 'timestamp': datetime.now().isoformat()},
                {'role': 'user', 'content': 'I forgot my password and can\'t log in', 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': 'No problem! I can help you reset your password. Can you please provide your email address or username?', 'timestamp': datetime.now().isoformat()},
                {'role': 'user', 'content': 'My email is john.doe@example.com', 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': 'Perfect! I\'ve sent a password reset link to john.doe@example.com. Please check your email and click on the link to create a new password.', 'timestamp': datetime.now().isoformat()},
                {'role': 'user', 'content': 'Thank you so much!', 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': 'You\'re welcome! If you need any further assistance, feel free to ask. Have a great day!', 'timestamp': datetime.now().isoformat()},
            ]
            st.session_state.call_messages[bot_name] = sample_messages
            st.rerun()
        
        st.markdown("---")
        
        # Show sample transcript display (non-interactive preview)
        sample_messages_preview = [
            {'role': 'user', 'content': 'Hello, I need help with my account', 'timestamp': '2024-01-15T10:00:00'},
            {'role': 'assistant', 'content': 'Hello! I\'d be happy to help you with your account. What specific issue are you experiencing?', 'timestamp': '2024-01-15T10:00:05'},
            {'role': 'user', 'content': 'I forgot my password and can\'t log in', 'timestamp': '2024-01-15T10:00:15'},
            {'role': 'assistant', 'content': 'No problem! I can help you reset your password. Can you please provide your email address or username?', 'timestamp': '2024-01-15T10:00:20'},
        ]
        
        for idx, msg in enumerate(sample_messages_preview):
            if msg['role'] == 'user':
                with st.container():
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.markdown(f"**👤 You:** {msg['content']}")
                    with col2:
                        st.caption(msg.get('timestamp', '')[:19] if 'timestamp' in msg else '')
            else:
                with st.container():
                    col1, col2, col3 = st.columns([8, 1, 1])
                    with col1:
                        st.markdown(f"**🤖 Bot:** {msg['content']}")
                    with col2:
                        st.button("👍", key=f"preview_like_{idx}", use_container_width=True, disabled=True)
                    with col3:
                        st.button("👎", key=f"preview_dislike_{idx}", use_container_width=True, disabled=True)
                    st.caption(msg.get('timestamp', '')[:19] if 'timestamp' in msg else '')
                    st.markdown("---")
        
        st.markdown("---")
        st.caption("💡 **Click the button above to load sample messages and test the like/dislike functionality!**")
        return
    
    # Real transcript display
    
    st.subheader("📝 Call Transcript")
    st.markdown("---")
    
    for idx, msg in enumerate(messages):
        if msg['role'] == 'user':
            with st.container():
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"**👤 You:** {msg['content']}")
                with col2:
                    st.caption(msg.get('timestamp', '')[:19] if 'timestamp' in msg else '')
        else:
            # Bot response with like/dislike
            with st.container():
                col1, col2, col3 = st.columns([8, 1, 1])
                with col1:
                    st.markdown(f"**🤖 Bot:** {msg['content']}")
                with col2:
                    # Like button
                    current_reaction = st.session_state.like_dislike_feedback.get(bot_name, {}).get(idx, None)
                    like_emoji = "👍" if current_reaction == 'like' else "👍"
                    like_type = "primary" if current_reaction == 'like' else "secondary"
                    
                    if st.button(like_emoji, key=f"like_{bot_name}_{idx}", use_container_width=True, type=like_type):
                        if current_reaction == 'like':
                            save_like_dislike(bot_name, idx, None)  # Toggle off
                        else:
                            save_like_dislike(bot_name, idx, 'like')
                        st.rerun()
                
                with col3:
                    # Dislike button
                    dislike_emoji = "👎" if current_reaction == 'dislike' else "👎"
                    dislike_type = "primary" if current_reaction == 'dislike' else "secondary"
                    
                    if st.button(dislike_emoji, key=f"dislike_{bot_name}_{idx}", use_container_width=True, type=dislike_type):
                        if current_reaction == 'dislike':
                            save_like_dislike(bot_name, idx, None)  # Toggle off
                            st.session_state.dislike_popup_open[bot_name] = None
                        else:
                            # Open popup to get reason for dislike
                            st.session_state.dislike_popup_open[bot_name] = idx
                        st.rerun()
                
                # Show dislike reason popup if this message is being disliked
                if st.session_state.dislike_popup_open.get(bot_name) == idx:
                    with st.container():
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
                            border: 2px solid #ff4a4a;
                            border-radius: 10px;
                            padding: 1.5rem;
                            margin: 1rem 0;
                            box-shadow: 0 5px 20px rgba(255, 74, 74, 0.3);
                        ">
                            <h4 style="color: #fafafa; margin-bottom: 1rem;">👎 Why did you dislike this response?</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        dislike_reason = st.text_area(
                            "Reason for dislike",
                            key=f"dislike_reason_{bot_name}_{idx}",
                            placeholder="Please explain why you disliked this response...",
                            height=80,
                            help="Your feedback helps improve the bot's responses"
                        )
                        
                        col_submit_reason, col_cancel_reason = st.columns(2)
                        with col_submit_reason:
                            if st.button("✅ Submit", key=f"submit_dislike_reason_{bot_name}_{idx}", use_container_width=True, type="primary"):
                                if dislike_reason.strip():
                                    save_like_dislike(bot_name, idx, 'dislike', dislike_reason.strip())
                                    st.session_state.dislike_popup_open[bot_name] = None
                                    st.success("Dislike reason saved!")
                                    st.rerun()
                                else:
                                    st.warning("Please provide a reason for disliking")
                        with col_cancel_reason:
                            if st.button("❌ Cancel", key=f"cancel_dislike_reason_{bot_name}_{idx}", use_container_width=True):
                                st.session_state.dislike_popup_open[bot_name] = None
                                st.rerun()
                
                # Show current reaction status
                if current_reaction:
                    reaction_text = "👍 Liked" if current_reaction == 'like' else "👎 Disliked"
                    st.caption(f"*{reaction_text}*")
                    
                    # Show dislike reason if available
                    if current_reaction == 'dislike' and bot_name in st.session_state.dislike_reasons and idx in st.session_state.dislike_reasons[bot_name]:
                        reason = st.session_state.dislike_reasons[bot_name][idx]
                        st.caption(f"💬 Reason: {reason}")
                
                st.caption(msg.get('timestamp', '')[:19] if 'timestamp' in msg else '')
                st.markdown("---")

def display_chat(bot_name: str, mode: str = 'chat'):
    """Display chat messages for selected bot"""
    if mode == 'chat':
        messages = st.session_state.bots[bot_name]['messages']
    else:
        messages = st.session_state.call_messages[bot_name]
    
    # Display messages
    for idx, msg in enumerate(messages):
        if msg['role'] == 'user':
            with st.chat_message("user"):
                if mode == 'call':
                    st.write("🎤 " + msg['content'])
                    if 'audio' in msg:
                        st.audio(msg['audio'], format='audio/wav')
                else:
                    st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                if mode == 'call':
                    st.write("🔊 " + msg['content'])
                    # TODO: Display audio playback here when backend is connected
                else:
                    st.write(msg['content'])
                
                # Feedback section for assistant messages
                col1, col2 = st.columns([1, 4])
                with col1:
                    # Check if feedback exists for this message
                    has_feedback = (bot_name in st.session_state.feedback and 
                                  idx in st.session_state.feedback[bot_name])
                    
                    if has_feedback:
                        feedback = st.session_state.feedback[bot_name][idx]
                        st.caption(f"⭐ {feedback['rating']}/5")
                        if st.button("✏️ Edit", key=f"edit_feedback_{bot_name}_{idx}_{mode}", use_container_width=True):
                            st.session_state.feedback_form_open = (idx, mode)
                            st.rerun()
                    else:
                        if st.button("💬 Feedback", key=f"feedback_{bot_name}_{idx}_{mode}", use_container_width=True):
                            st.session_state.feedback_form_open = (idx, mode)
                            st.rerun()
                
                # Show feedback form if this message is selected
                if st.session_state.feedback_form_open and st.session_state.feedback_form_open[0] == idx and st.session_state.feedback_form_open[1] == mode:
                    with st.expander("📝 Provide Feedback", expanded=True):
                        rating = st.slider(
                            "Rating",
                            min_value=1,
                            max_value=5,
                            value=st.session_state.feedback[bot_name].get(idx, {}).get('rating', 3) if has_feedback else 3,
                            key=f"rating_{bot_name}_{idx}_{mode}"
                        )
                        comment = st.text_area(
                            "Comments (optional)",
                            value=st.session_state.feedback[bot_name].get(idx, {}).get('comment', '') if has_feedback else '',
                            key=f"comment_{bot_name}_{idx}_{mode}",
                            placeholder="Share your thoughts about this response..."
                        )
                        
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.button("✅ Submit", key=f"submit_{bot_name}_{idx}_{mode}", use_container_width=True):
                                save_feedback(bot_name, idx, rating, comment)
                                st.session_state.feedback_form_open = None
                                st.success("Feedback saved!")
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{bot_name}_{idx}_{mode}", use_container_width=True):
                                st.session_state.feedback_form_open = None
                                st.rerun()

def render_plato_home_page():
    """Render PLATO-style home page with simulation cards - side by side horizontal layout"""
    
    # CSS for horizontal scrolling cards
    st.markdown("""
    <style>
        .home-welcome {
            margin-bottom: 1.5rem;
            padding: 0 1rem;
        }
        
        .home-welcome h1 {
            color: #fafafa;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .home-welcome p {
            color: #b0b0b0;
            font-size: 1.1rem;
        }
        
        .home-card {
            background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid rgba(74, 158, 255, 0.2);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            height: 380px;
        }
        
        .home-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(74, 158, 255, 0.3);
            border-color: #4a9eff;
        }
        
        .home-card-tag {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            background: rgba(74, 158, 255, 0.2);
            color: #4a9eff;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            width: fit-content;
        }
        
        .home-card-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4a9eff 0%, #3a8eef 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            border: 3px solid #4a9eff;
            box-shadow: 0 0 20px rgba(74, 158, 255, 0.4);
            margin: 0 auto 0.75rem auto;
        }
        
        .home-card-title {
            color: #fafafa;
            font-size: 1.1rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.25rem;
            line-height: 1.3;
        }
        
        .home-card-name {
            color: #b0b0b0;
            font-size: 0.8rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .home-card-description {
            color: #d0d0d0;
            font-size: 0.75rem;
            text-align: center;
            line-height: 1.4;
            flex-grow: 1;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Welcome header
    st.markdown("""
    <div class="home-welcome">
        <h1>🤖 Chatbot Evaluation Platform</h1>
        <p>Select a simulation below to start a call or view the profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create all cards side by side in one row using st.columns
    bot_list = list(st.session_state.bots.items())
    cols = st.columns(len(bot_list))
    
    for idx, (bot_name, bot_data) in enumerate(bot_list):
        avatar_emoji = bot_data.get('avatar_emoji', '🤖')
        display_name = bot_data.get('display_name', bot_name)
        person_name = bot_data.get('person_name', '')
        description = bot_data.get('description', '')
        bot_type = bot_data.get('type', bot_data.get('customer_segment', 'Simulation'))
        
        with cols[idx]:
            # Card HTML
            st.markdown(f"""
            <div class="home-card">
                <span class="home-card-tag">{bot_type}</span>
                <div class="home-card-avatar">{avatar_emoji}</div>
                <div class="home-card-title">{display_name}</div>
                <div class="home-card-name">{person_name}</div>
                <div class="home-card-description">{description}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Streamlit buttons (work properly with Streamlit's state)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📞 Call", key=f"home_call_{bot_name}", use_container_width=True, type="primary"):
                    st.session_state.selected_bot = bot_name
                    st.session_state.view_mode = 'bot_detail'
                    st.session_state.bot_modes[bot_name] = 'call'
                    st.rerun()
            with btn_col2:
                if st.button("👤 Profile", key=f"home_profile_{bot_name}", use_container_width=True):
                    st.session_state.selected_bot = bot_name
                    st.session_state.view_mode = 'bot_detail'
                    st.rerun()

def main():
    # Check if we're in call mode to show sidebar
    is_call_mode = (
        st.session_state.view_mode == 'bot_detail' and 
        st.session_state.selected_bot and 
        st.session_state.bot_modes.get(st.session_state.selected_bot) == 'call'
    )
    
    # Only show sidebar on call page
    if is_call_mode:
        with st.sidebar:
            # Custom CSS for icon buttons
            st.markdown("""
            <style>
                .sidebar-icon {
                    width: 50px;
                    height: 50px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.8rem;
                    margin: 0.5rem auto;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    background: transparent;
                    text-decoration: none;
                }
                .sidebar-icon:hover {
                    background: rgba(74, 158, 255, 0.2);
                }
                .sidebar-icon.active {
                    background: rgba(74, 158, 255, 0.3);
                }
                .sidebar-spacer {
                    flex: 1;
                    min-height: 150px;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Home button
            if st.button("🏠 Home", key="sidebar_home", use_container_width=True):
                st.session_state.view_mode = 'home'
                st.session_state.selected_bot = None
                st.rerun()
    
    # Handle query parameters for button clicks
    query_params = st.query_params
    if 'bot' in query_params and 'action' in query_params:
        bot_name = query_params['bot']
        action = query_params['action']
        if bot_name in st.session_state.bots:
            # Only process if not already set to avoid loops
            if st.session_state.selected_bot != bot_name or st.session_state.view_mode != 'bot_detail':
                st.session_state.selected_bot = bot_name
                st.session_state.view_mode = 'bot_detail'
                if action == 'call':
                    st.session_state.bot_modes[bot_name] = 'call'
                else:
                    st.session_state.bot_modes[bot_name] = 'chat'  # Profile shows chat mode
                # Clear query parameters and rerun
                del st.query_params['bot']
                del st.query_params['action']
                st.rerun()
    
    # Main content area - Show home page or bot detail
    if st.session_state.view_mode == 'home':
        # Show PLATO home page with cards
        render_plato_home_page()
        return
    
    # Bot detail view - Main content area
    current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
    
    # Check if Vapi is configured
    config = st.session_state.api_configs[st.session_state.selected_bot]
    use_vapi = config.get('use_vapi', False) and config.get('assistant_id') and config.get('vapi_api_key')
    
    if current_mode == 'call':
        # Render the beautiful call interface
        render_call_interface(st.session_state.selected_bot)
        # Call interface has its own feedback box, so we return early
        return
    
    elif current_mode == 'chat':
        # Chat mode - show title and chat interface
        st.title(f"💬 {st.session_state.selected_bot} - Chat")
        st.caption(st.session_state.bots[st.session_state.selected_bot]['description'])
        st.markdown("---")
        
        if use_vapi:
            st.info("🎤 **Vapi Active** - Use the Vapi widget below to interact with the bot")
            render_vapi_widget(
                st.session_state.selected_bot,
                current_mode,
                config.get('assistant_id', ''),
                config.get('vapi_api_key', '')
            )
        else:
            display_chat(st.session_state.selected_bot, current_mode)
    
    
    # Session Feedback Section (appears after user has chatted/called)
    current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
    if current_mode == 'chat':
        messages = st.session_state.bots[st.session_state.selected_bot]['messages']
    else:
        messages = st.session_state.call_messages[st.session_state.selected_bot]
    
    has_messages = len(messages) > 0
    has_session_feedback = st.session_state.selected_bot in st.session_state.session_feedback
    call_ended = current_mode == 'call' and st.session_state.call_status.get(st.session_state.selected_bot) == 'ended'
    call_feedback = st.session_state.call_overall_feedback.get(st.session_state.selected_bot)
    
    # Show feedback if there are messages OR if call has ended
    if has_messages or call_ended:
        # Handle call feedback after popup interaction
        if call_ended and call_feedback == 'like':
            st.success("👍 **Thank you!** You liked this call.")
            if st.button("💬 Provide Detailed Feedback", use_container_width=True):
                st.session_state.session_feedback_form_open = True
                st.rerun()
            st.markdown("---")
        
        # Show session feedback section
        if not has_session_feedback and not st.session_state.session_feedback_form_open:
            if not call_ended or (call_ended and st.session_state.call_overall_feedback.get(st.session_state.selected_bot) != 'dislike'):
                if call_ended:
                    # This won't show if dislike was clicked (form opens automatically)
                    pass
                else:
                    st.info("💡 **Finished chatting?** Please provide your overall feedback on this session!")
                    if st.button("📝 Submit Session Feedback", use_container_width=True, type="primary"):
                        st.session_state.session_feedback_form_open = True
                        st.rerun()
        
        # Session feedback form (only show if NOT in popup mode)
        # Skip showing feedback form here if it's already shown in popup
        show_feedback_in_popup = call_ended and st.session_state.call_overall_feedback.get(st.session_state.selected_bot) == 'dislike' and st.session_state.session_feedback_form_open
        
        if (st.session_state.session_feedback_form_open or has_session_feedback) and not show_feedback_in_popup:
            with st.container():
                if call_ended:
                    # For call mode: Show transcript with like/dislike AND paragraph feedback
                    st.subheader("📞 Call Feedback")
                    
                    # Tab 1: Transcript with Like/Dislike
                    tab1, tab2 = st.tabs(["📝 Transcript Feedback", "💬 Paragraph Feedback"])
                    
                    with tab1:
                        st.markdown("### Rate each bot response:")
                        display_call_transcript(st.session_state.selected_bot)
                        
                        # Summary of reactions
                        like_dislike_data = st.session_state.like_dislike_feedback.get(st.session_state.selected_bot, {})
                        if like_dislike_data:
                            likes = sum(1 for v in like_dislike_data.values() if v == 'like')
                            dislikes = sum(1 for v in like_dislike_data.values() if v == 'dislike')
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("👍 Liked", likes)
                            with col2:
                                st.metric("👎 Disliked", dislikes)
                    
                    with tab2:
                        # Paragraph feedback
                        if has_session_feedback:
                            st.success("✅ Paragraph feedback submitted!")
                            session_fb = st.session_state.session_feedback[st.session_state.selected_bot]
                            st.caption(f"Rating: ⭐ {session_fb['rating']}/5")
                            if session_fb['comment']:
                                st.write(f"**Comment:** {session_fb['comment']}")
                            if st.button("✏️ Edit Paragraph Feedback", use_container_width=True):
                                st.session_state.session_feedback_form_open = True
                                st.rerun()
                        else:
                            st.markdown("### 💬 Overall Call Feedback")
                            st.caption("How would you rate your overall experience with this call?")
                            
                            session_rating = st.slider(
                                "Overall Rating",
                                min_value=1,
                                max_value=5,
                                value=3,
                                key="session_rating",
                                help="Rate your overall experience from 1 (poor) to 5 (excellent)"
                            )
                            
                            session_comment = st.text_area(
                                "Overall Comments",
                                key="session_comment",
                                placeholder="Share your overall thoughts about this call. What did you like? What could be improved?",
                                height=100
                            )
                            
                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                if st.button("✅ Submit Paragraph Feedback", key="submit_session_feedback", use_container_width=True, type="primary"):
                                    save_session_feedback(st.session_state.selected_bot, session_rating, session_comment)
                                    reset_session_for_bot(st.session_state.selected_bot)
                                    st.success("✅ Thank you for your feedback! 🎉 Starting a new session...")
                                    st.rerun()
                            with col_cancel:
                                if st.button("❌ Cancel", key="cancel_session_feedback", use_container_width=True):
                                    st.session_state.session_feedback_form_open = False
                                    st.rerun()
                else:
                    # For chat mode: Regular feedback
                    if has_session_feedback:
                        st.success("✅ Session feedback submitted!")
                        session_fb = st.session_state.session_feedback[st.session_state.selected_bot]
                        st.caption(f"Rating: ⭐ {session_fb['rating']}/5")
                        if session_fb['comment']:
                            st.caption(f"Comment: {session_fb['comment']}")
                        if st.button("✏️ Edit Session Feedback", use_container_width=True):
                            st.session_state.session_feedback_form_open = True
                            st.rerun()
                    else:
                        st.subheader("📝 Overall Session Feedback")
                        st.caption("How would you rate your overall experience with this chatbot?")
                        
                        session_rating = st.slider(
                            "Overall Rating",
                            min_value=1,
                            max_value=5,
                            value=3,
                            key="session_rating",
                            help="Rate your overall experience from 1 (poor) to 5 (excellent)"
                        )
                        
                        session_comment = st.text_area(
                            "Overall Comments",
                            key="session_comment",
                            placeholder="Share your overall thoughts about this chatbot session. What did you like? What could be improved?",
                            height=100
                        )
                        
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.button("✅ Submit Feedback", key="submit_session_feedback", use_container_width=True, type="primary"):
                                save_session_feedback(st.session_state.selected_bot, session_rating, session_comment)
                                reset_session_for_bot(st.session_state.selected_bot)
                                st.success("✅ Thank you for your feedback! 🎉 Starting a new session...")
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", key="cancel_session_feedback", use_container_width=True):
                                st.session_state.session_feedback_form_open = False
                                st.rerun()
        
        st.markdown("---")
    
    # Input section based on mode (only show if Vapi is not active)
    current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
    config = st.session_state.api_configs[st.session_state.selected_bot]
    use_vapi = config.get('use_vapi', False) and config.get('assistant_id') and config.get('vapi_api_key')
    
    if not use_vapi:
        # Fallback to Streamlit native input when Vapi is not configured
        if current_mode == 'chat':
            # Chat input
            user_input = st.chat_input(f"Message {st.session_state.selected_bot}...")
            
            if user_input:
                send_message(st.session_state.selected_bot, user_input, 'chat')
                # Reset session feedback form state when new message is sent
                if st.session_state.feedback_form_open:
                    st.session_state.feedback_form_open = None
                st.rerun()
        else:
            # Call mode - interface already shown
            pass
    else:
        # Vapi handles input via its widget
        st.caption("💡 Use the Vapi widget above to interact with the bot")

if __name__ == "__main__":
    main()
