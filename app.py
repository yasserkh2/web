import streamlit as st
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="Chatbot Evaluation Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Additional dark mode CSS for better visibility and PLATO-style UI
st.markdown("""
<style>
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
    
    /* PLATO-style Sidebar */
    .plato-sidebar {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d2e 100%);
        padding: 1.5rem 1rem;
    }
    
    .plato-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .plato-logo-triangle {
        width: 0;
        height: 0;
        border-left: 20px solid transparent;
        border-right: 20px solid transparent;
        border-bottom: 35px solid #4a9eff;
        position: relative;
    }
    
    .plato-logo-text {
        display: flex;
        flex-direction: column;
        color: #fafafa;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .plato-nav-icons {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .plato-nav-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        background: rgba(74, 158, 255, 0.1);
        color: #4a9eff;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .plato-nav-icon:hover {
        background: rgba(74, 158, 255, 0.2);
        transform: scale(1.1);
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
    
    /* Footer */
    .plato-footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        gap: 2rem;
    }
    
    .plato-footer-link {
        color: #b0b0b0;
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s ease;
    }
    
    .plato-footer-link:hover {
        color: #4a9eff;
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

def render_call_interface(bot_name: str):
    """Render the call interface UI using Streamlit components"""
    bot_data = st.session_state.bots.get(bot_name, {})
    call_status = st.session_state.call_status.get(bot_name, 'idle')
    
    display_name = bot_data.get('display_name', bot_name)
    person_name = bot_data.get('person_name', '')
    avatar_emoji = bot_data.get('avatar_emoji', '🤖')
    description = bot_data.get('description', '')
    
    # Status text
    status_text = {
        'idle': '📞 Ready to Call',
        'ringing': '📞 Connecting...',
        'active': '✅ Call Active',
        'ended': '📴 Call Ended'
    }.get(call_status, 'Ready')
    
    # Header
    st.markdown(f"### 📞 {display_name}")
    if person_name:
        st.caption(person_name)
    
    st.markdown("---")
    
    # Avatar and status - centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">{avatar_emoji}</div>
            <h2 style="color: #fafafa; margin: 0.5rem 0;">{display_name}</h2>
            <p style="color: #b0b0b0;">{person_name}</p>
            <p style="color: #4a9eff; font-weight: bold; margin-top: 1rem;">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Control buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col2:
        if st.button("🔄 Retry", key="call_retry", use_container_width=True):
            st.session_state.call_status[bot_name] = 'idle'
            st.rerun()
    
    with col3:
        mute_label = "🔇 Unmute" if st.session_state.get(f'muted_{bot_name}', False) else "🎤 Mute"
        if st.button(mute_label, key="call_mute", use_container_width=True):
            st.session_state[f'muted_{bot_name}'] = not st.session_state.get(f'muted_{bot_name}', False)
            st.rerun()
    
    with col4:
        # Main call button
        if call_status == 'idle' or call_status == 'ended':
            if st.button("📞 Start Call", key="call_start", type="primary", use_container_width=True):
                st.session_state.call_status[bot_name] = 'active'
                st.session_state.active_calls[bot_name] = f"call_{datetime.now().timestamp()}"
                st.rerun()
        elif call_status == 'ringing':
            if st.button("❌ Cancel", key="call_cancel", use_container_width=True):
                st.session_state.call_status[bot_name] = 'idle'
                st.session_state.active_calls.pop(bot_name, None)
                st.rerun()
        else:  # active
            if st.button("📴 End Call", key="call_end", type="primary", use_container_width=True):
                st.session_state.call_status[bot_name] = 'ended'
                st.session_state.active_calls.pop(bot_name, None)
                st.session_state.show_feedback_popup[bot_name] = True
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

def render_plato_home_page():
    """Render PLATO-style home page with simulation cards"""
    # Welcome section
    st.markdown("""
    <div class="plato-welcome">
        <h1 class="plato-welcome-title">Welcome to PLATO</h1>
        <p class="plato-welcome-subtitle">Choose an avatar and learn or practice your skills in a realistic simulation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cards container
    st.markdown('<div class="plato-cards-container">', unsafe_allow_html=True)
    
    # Create cards for each bot
    cols = st.columns(len(st.session_state.bots))
    for idx, (bot_name, bot_data) in enumerate(st.session_state.bots.items()):
        with cols[idx]:
            # Card HTML
            card_html = f"""
            <div class="plato-card">
                <div class="plato-card-tag">{bot_data.get('type', 'Simulation')}</div>
                <div class="plato-card-profile">
                    <div class="plato-card-halo"></div>
                    <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #4a9eff 0%, #3a8eef 100%); display: flex; align-items: center; justify-content: center; font-size: 4rem; border: 3px solid #4a9eff; position: relative; z-index: 2;">
                        {bot_data.get('avatar_emoji', '🤖')}
                    </div>
                </div>
                <h3 class="plato-card-title">{bot_data.get('display_name', bot_name)}</h3>
                <p class="plato-card-name">{bot_data.get('person_name', '')}</p>
                <p class="plato-card-description">{bot_data.get('description', '')}</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Start Call", key=f"start_{bot_name}", use_container_width=True, type="primary"):
                    st.session_state.selected_bot = bot_name
                    st.session_state.view_mode = 'bot_detail'
                    st.session_state.bot_modes[bot_name] = 'call'
                    st.rerun()
            with col2:
                if st.button("See Profile", key=f"profile_{bot_name}", use_container_width=True):
                    st.session_state.selected_bot = bot_name
                    st.session_state.view_mode = 'bot_detail'
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="plato-footer">
        <a href="#" class="plato-footer-link">Terms of Services</a>
        <a href="#" class="plato-footer-link">Privacy Policy</a>
    </div>
    """, unsafe_allow_html=True)

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
    """Render PLATO-style home page with simulation cards"""
    # Welcome section
    st.markdown("""
    <div class="plato-welcome">
        <h1 class="plato-welcome-title">Welcome to PLATO</h1>
        <p class="plato-welcome-subtitle">Choose an avatar and learn or practice your skills in a realistic simulation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Build all cards HTML in one container for horizontal scrolling
    # Use components.html for proper HTML rendering
    import streamlit.components.v1 as components
    
    cards_html = '''
    <style>
        .cards-scroll-container {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            gap: 1.5rem;
            padding: 1rem 0 1.5rem 0;
            width: 100%;
            align-items: stretch;
        }
        .cards-scroll-container::-webkit-scrollbar {
            height: 10px;
        }
        .cards-scroll-container::-webkit-scrollbar-track {
            background: #1e2130;
            border-radius: 5px;
        }
        .cards-scroll-container::-webkit-scrollbar-thumb {
            background: #4a9eff;
            border-radius: 5px;
        }
        .card-wrapper {
            flex: 0 0 280px !important;
            min-width: 280px !important;
            max-width: 280px !important;
            height: 420px;
        }
        .card {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid rgba(74, 158, 255, 0.2);
            transition: all 0.3s ease;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(74, 158, 255, 0.3);
            border-color: #4a9eff;
        }
        .card-tag {
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
        .card-avatar-wrapper {
            display: flex;
            justify-content: center;
            margin-bottom: 0.75rem;
        }
        .card-avatar {
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
        .card-title {
            color: #fafafa;
            font-size: 1.1rem;
            font-weight: bold;
            margin: 0.5rem 0 0.25rem 0;
            text-align: center;
            line-height: 1.3;
        }
        .card-name {
            color: #b0b0b0;
            font-size: 0.8rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .card-description {
            color: #d0d0d0;
            font-size: 0.75rem;
            text-align: center;
            margin-bottom: 1rem;
            line-height: 1.4;
            flex-grow: 1;
            overflow: hidden;
        }
        .card-buttons {
            margin-top: auto;
            width: 100%;
            display: flex;
            gap: 0.5rem;
        }
        .card-btn {
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
        .card-btn-primary {
            background: #4a9eff;
            color: #fafafa;
        }
        .card-btn-primary:hover {
            background: #3a8eef;
            transform: scale(1.02);
        }
        .card-btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fafafa;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
    <div class="cards-scroll-container">
    '''
    
    for bot_name, bot_data in st.session_state.bots.items():
        avatar_emoji = bot_data.get('avatar_emoji', '🤖')
        display_name = bot_data.get('display_name', bot_name)
        person_name = bot_data.get('person_name', '')
        description = bot_data.get('description', '')
        bot_type = bot_data.get('type', bot_data.get('customer_segment', 'Simulation'))
        # Escape quotes in bot_name for JavaScript
        safe_bot_name = bot_name.replace("'", "\\'")
        
        cards_html += f'''<div class="card-wrapper"><div class="card"><span class="card-tag">{bot_type}</span><div class="card-avatar-wrapper"><div class="card-avatar">{avatar_emoji}</div></div><h3 class="card-title">{display_name}</h3><p class="card-name">{person_name}</p><p class="card-description">{description}</p><div class="card-buttons"><button class="card-btn card-btn-primary" onclick="window.parent.postMessage({{type: 'streamlit:setQueryParam', bot: '{safe_bot_name}', action: 'call'}}, '*'); window.location.href='?bot={safe_bot_name}&action=call';">Start Call</button><button class="card-btn card-btn-secondary" onclick="window.location.href='?bot={safe_bot_name}&action=profile';">See Profile</button></div></div></div>'''
    
    cards_html += '</div>'
    
    # Use components.html for reliable HTML rendering
    components.html(cards_html, height=460, scrolling=True)
    
    # Footer
    st.markdown("""
    <div class="plato-footer">
        <a href="#" class="plato-footer-link">Terms of Services</a>
        <a href="#" class="plato-footer-link">Privacy Policy</a>
    </div>
    """, unsafe_allow_html=True)

def render_plato_sidebar():
    """Render PLATO-style sidebar with logo and navigation"""
    st.markdown("""
    <div class="plato-sidebar">
        <div class="plato-logo">
            <div class="plato-logo-triangle"></div>
            <div class="plato-logo-text">
                <span>CTC</span>
                <span style="font-size: 0.9rem; margin-top: -5px;">HEALTH</span>
            </div>
        </div>
        <div class="plato-nav-icons">
            <div class="plato-nav-icon">📊</div>
            <div class="plato-nav-icon">👤</div>
            <div class="plato-nav-icon">📤</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Home button
    if st.button("🏠 Home", use_container_width=True, key="home_button"):
        st.session_state.view_mode = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # Bot selection (only show in bot detail view)
    if st.session_state.view_mode == 'bot_detail':
        st.subheader("Select Bot")
        for bot_name in st.session_state.bots.keys():
            is_selected = st.session_state.selected_bot == bot_name
            if st.button(
                bot_name,
                key=f"bot_{bot_name}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_bot = bot_name
                st.session_state.view_mode = 'bot_detail'
                st.rerun()
        
        st.markdown("---")
        
        # Mode selection (Chat/Call) for selected bot
        st.subheader("📞 Communication Mode")
        mode = st.radio(
            "Select Mode",
            options=['chat', 'call'],
            format_func=lambda x: '💬 Chat' if x == 'chat' else '📞 Call',
            index=0 if st.session_state.bot_modes[st.session_state.selected_bot] == 'chat' else 1,
            key=f"mode_selector_{st.session_state.selected_bot}"
        )
        if mode != st.session_state.bot_modes[st.session_state.selected_bot]:
            st.session_state.bot_modes[st.session_state.selected_bot] = mode
            st.rerun()
        
        st.markdown("---")
        
        # Bot configuration - Vapi Settings
        with st.expander("⚙️ Bot Settings - Vapi", expanded=False):
            selected_bot_config = st.selectbox(
                "Configure Bot",
                options=list(st.session_state.bots.keys()),
                index=list(st.session_state.bots.keys()).index(st.session_state.selected_bot),
                key="sidebar_bot_config_select"
            )
            
            config = st.session_state.api_configs[selected_bot_config]
            
            # Enable/Disable Vapi
            use_vapi = st.checkbox(
                "Enable Vapi",
                value=config.get('use_vapi', False),
                key=f"use_vapi_{selected_bot_config}",
                help="Enable Vapi frontend integration for this bot"
            )
            
            if use_vapi:
                vapi_api_key = st.text_input(
                    "Vapi API Key",
                    value=config.get('vapi_api_key', ''),
                    key=f"vapi_api_key_{selected_bot_config}",
                    type="password",
                    help="Your Vapi API key"
                )
                
                assistant_id = st.text_input(
                    "Assistant ID",
                    value=config.get('assistant_id', ''),
                    key=f"assistant_id_{selected_bot_config}",
                    help="Vapi Assistant ID for this bot"
                )
                
                phone_number_id = st.text_input(
                    "Phone Number ID (Optional)",
                    value=config.get('phone_number_id', ''),
                    key=f"phone_number_id_{selected_bot_config}",
                    help="Vapi Phone Number ID for call mode (optional)"
                )
                
                server_url = st.text_input(
                    "Vapi Server URL",
                    value=config.get('server_url', 'https://api.vapi.ai'),
                    key=f"server_url_{selected_bot_config}",
                    help="Vapi API server URL"
                )
                
                # Save config
                st.session_state.api_configs[selected_bot_config]['use_vapi'] = use_vapi
                st.session_state.api_configs[selected_bot_config]['vapi_api_key'] = vapi_api_key
                st.session_state.api_configs[selected_bot_config]['assistant_id'] = assistant_id
                st.session_state.api_configs[selected_bot_config]['phone_number_id'] = phone_number_id
                st.session_state.api_configs[selected_bot_config]['server_url'] = server_url
                
                if vapi_api_key and assistant_id:
                    st.success("✅ Vapi configured!")
                else:
                    st.warning("⚠️ Please provide API Key and Assistant ID")
            else:
                st.session_state.api_configs[selected_bot_config]['use_vapi'] = False
        
        st.markdown("---")
        
        # Clear chat/call button
        current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
        if st.button("🗑️ Clear History", use_container_width=True, key="sidebar_clear_history"):
            if current_mode == 'chat':
                st.session_state.bots[st.session_state.selected_bot]['messages'] = []
            else:
                st.session_state.call_messages[st.session_state.selected_bot] = []
            st.rerun()
        
        # Export chat/call history
        current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
        if st.button("💾 Export History", use_container_width=True, key="sidebar_export_history"):
            if current_mode == 'chat':
                messages = st.session_state.bots[st.session_state.selected_bot]['messages']
                file_prefix = "chat"
            else:
                messages = st.session_state.call_messages[st.session_state.selected_bot]
                file_prefix = "call"
            
            feedback_data = st.session_state.feedback.get(st.session_state.selected_bot, {})
            session_feedback_data = st.session_state.session_feedback.get(st.session_state.selected_bot)
            like_dislike_data = st.session_state.like_dislike_feedback.get(st.session_state.selected_bot, {})
            dislike_reasons_data = st.session_state.dislike_reasons.get(st.session_state.selected_bot, {})
            export_data = {
                'bot_name': st.session_state.selected_bot,
                'mode': current_mode,
                'messages': messages,
                'message_feedback': feedback_data,
                'like_dislike_feedback': like_dislike_data,
                'dislike_reasons': dislike_reasons_data,
                'session_feedback': session_feedback_data,
                'exported_at': datetime.now().isoformat()
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"{file_prefix}_{st.session_state.selected_bot}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.markdown("---")
        
        # View Feedback section
        with st.expander("📊 View All Feedback", expanded=False):
            # Session feedback
            session_fb = st.session_state.session_feedback.get(st.session_state.selected_bot)
            if session_fb:
                st.markdown("**🎯 Overall Session Feedback:**")
                st.caption(f"⭐ Rating: {session_fb['rating']}/5")
                if session_fb['comment']:
                    st.write(f"💬 Comment: {session_fb['comment']}")
                st.caption(f"📅 {session_fb['timestamp']}")
                st.markdown("---")
            
            # Message-level feedback
            bot_feedback = st.session_state.feedback.get(st.session_state.selected_bot, {})
            if bot_feedback:
                st.markdown("**💬 Message Feedback:**")
                for msg_idx, feedback_data in bot_feedback.items():
                    if msg_idx < len(st.session_state.bots[st.session_state.selected_bot]['messages']):
                        msg = st.session_state.bots[st.session_state.selected_bot]['messages'][msg_idx]
                        if msg['role'] == 'assistant':
                            st.markdown(f"**Message {msg_idx//2 + 1}:**")
                            st.caption(f"⭐ Rating: {feedback_data['rating']}/5")
                            if feedback_data['comment']:
                                st.write(f"💬 Comment: {feedback_data['comment']}")
                            st.caption(f"📅 {feedback_data['timestamp']}")
                            st.markdown("---")
            
            if not session_fb and not bot_feedback:
                st.info("No feedback submitted yet.")

def main():
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
    
    # PLATO-style Sidebar
    with st.sidebar:
        render_plato_sidebar()
    
    # Main content area - Show home page or bot detail
    if st.session_state.view_mode == 'home':
        # Show PLATO home page with cards
        render_plato_home_page()
        return
    
    # Bot detail view - Main chat/call area
    col1, col2 = st.columns([3, 1])
    
    current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
    mode_icon = "💬" if current_mode == 'chat' else "📞"
    mode_name = "Chat" if current_mode == 'chat' else "Call"
    
    # Check for call feedback popup first (before other content)
    call_ended_popup = current_mode == 'call' and st.session_state.call_status.get(st.session_state.selected_bot) == 'ended'
    show_popup = st.session_state.show_feedback_popup.get(st.session_state.selected_bot, False)
    call_feedback_popup = st.session_state.call_overall_feedback.get(st.session_state.selected_bot)
    
    with col1:
        # Show popup at the very top if call ended
        if call_ended_popup and show_popup:
            # Check if dislike was clicked and show feedback form in popup
            show_feedback_in_popup = call_feedback_popup == 'dislike' and st.session_state.session_feedback_form_open
            
            # Create prominent popup-style feedback section at the top with auto-scroll
            st.markdown("""
            <div id="call-feedback-popup" style="
                background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
                border: 3px solid #4a9eff;
                border-radius: 15px;
                padding: 2rem;
                margin: 1rem 0;
                box-shadow: 0 10px 40px rgba(74, 158, 255, 0.3);
                text-align: center;
            ">
                <h2 style="color: #fafafa; margin-bottom: 1rem; font-size: 2rem;">📞 Call Ended</h2>
                <p style="color: #fafafa; font-size: 1.3rem; margin-bottom: 2rem;">How was your call experience?</p>
            </div>
            <script>
                // Auto-scroll to popup when it appears
                setTimeout(function() {
                    const popup = document.getElementById('call-feedback-popup');
                    if (popup) {
                        popup.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 100);
            </script>
            """, unsafe_allow_html=True)
            
            # Show feedback form in popup if dislike was clicked
            if show_feedback_in_popup:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📞 Call Feedback")
                
                # Tab 1: Transcript with Like/Dislike
                tab1_popup, tab2_popup = st.tabs(["📝 Transcript Feedback", "💬 Paragraph Feedback"])
                
                with tab1_popup:
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
                
                with tab2_popup:
                    st.markdown("### 💬 Overall Call Feedback")
                    st.caption("How would you rate your overall experience with this call?")
                    
                    session_rating = st.slider(
                        "Overall Rating",
                        min_value=1,
                        max_value=5,
                        value=3,
                        key="popup_session_rating",
                        help="Rate your overall experience from 1 (poor) to 5 (excellent)"
                    )
                    
                    session_comment = st.text_area(
                        "Overall Comments",
                        key="popup_session_comment",
                        placeholder="Share your overall thoughts about this call. What did you like? What could be improved?",
                        height=100
                    )
                    
                    col_submit_popup, col_cancel_popup = st.columns(2)
                    with col_submit_popup:
                        if st.button("✅ Submit Feedback", use_container_width=True, type="primary", key="submit_popup_feedback"):
                            save_session_feedback(st.session_state.selected_bot, session_rating, session_comment)
                            reset_session_for_bot(st.session_state.selected_bot)
                            st.success("✅ Thank you for your feedback! 🎉 Starting a new session...")
                            st.rerun()
                    with col_cancel_popup:
                        if st.button("❌ Cancel", use_container_width=True, key="cancel_popup_feedback"):
                            st.session_state.session_feedback_form_open = False
                            st.session_state.call_overall_feedback[st.session_state.selected_bot] = None
                            st.rerun()
            
            # Show feedback buttons if feedback not submitted yet
            if call_feedback_popup is None:
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_popup1, col_popup2, col_popup3 = st.columns([1, 2, 1])
                with col_popup2:
                    button_col1, button_col2 = st.columns(2)
                    with button_col1:
                        if st.button("👍 Like", use_container_width=True, type="primary", key="call_like_popup_top"):
                            st.session_state.call_overall_feedback[st.session_state.selected_bot] = 'like'
                            st.session_state.show_feedback_popup[st.session_state.selected_bot] = False
                            # Reset call status to idle to "go to home"
                            st.session_state.call_status[st.session_state.selected_bot] = 'idle'
                            st.rerun()
                    
                    with button_col2:
                        if st.button("👎 Dislike", use_container_width=True, type="primary", key="call_dislike_popup_top"):
                            st.session_state.call_overall_feedback[st.session_state.selected_bot] = 'dislike'
                            # Keep popup open and show feedback form
                            st.session_state.session_feedback_form_open = True
                            st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
        
        # Check if Vapi is configured
        config = st.session_state.api_configs[st.session_state.selected_bot]
        use_vapi = config.get('use_vapi', False) and config.get('assistant_id') and config.get('vapi_api_key')
        
        if current_mode == 'call':
            # Render the beautiful call interface
            render_call_interface(st.session_state.selected_bot)
            
            # Add test messages button for demo
            call_status = st.session_state.call_status.get(st.session_state.selected_bot, 'idle')
            if call_status == 'active':
                st.markdown("---")
                if st.button("🧪 Add Test Messages", use_container_width=True, help="Add sample messages to test like/dislike functionality", key="add_test_msgs"):
                    if not st.session_state.call_messages[st.session_state.selected_bot]:
                        test_messages = [
                            {'role': 'user', 'content': 'Hello, I need help with my account', 'timestamp': datetime.now().isoformat()},
                            {'role': 'assistant', 'content': 'Hello! I\'d be happy to help you with your account. What specific issue are you experiencing?', 'timestamp': datetime.now().isoformat()},
                            {'role': 'user', 'content': 'I forgot my password and can\'t log in', 'timestamp': datetime.now().isoformat()},
                            {'role': 'assistant', 'content': 'No problem! I can help you reset your password. Can you please provide your email address or username?', 'timestamp': datetime.now().isoformat()},
                            {'role': 'user', 'content': 'My email is john.doe@example.com', 'timestamp': datetime.now().isoformat()},
                            {'role': 'assistant', 'content': 'Perfect! I\'ve sent a password reset link to john.doe@example.com. Please check your email and click on the link to create a new password.', 'timestamp': datetime.now().isoformat()},
                            {'role': 'user', 'content': 'Thank you so much!', 'timestamp': datetime.now().isoformat()},
                            {'role': 'assistant', 'content': 'You\'re welcome! If you need any further assistance, feel free to ask. Have a great day!', 'timestamp': datetime.now().isoformat()},
                        ]
                        st.session_state.call_messages[st.session_state.selected_bot] = test_messages
                        st.success("Test messages added! You can now test like/dislike.")
                        st.rerun()
                    else:
                        st.info("Messages already exist. Clear history first to add test messages.")
                
                st.markdown("---")
                display_call_transcript(st.session_state.selected_bot)
        
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
    
    with col2:
        st.subheader("📊 Stats")
        current_mode = st.session_state.bot_modes[st.session_state.selected_bot]
        if current_mode == 'chat':
            messages = st.session_state.bots[st.session_state.selected_bot]['messages']
        else:
            messages = st.session_state.call_messages[st.session_state.selected_bot]
        
        user_messages = [m for m in messages if m['role'] == 'user']
        bot_messages = [m for m in messages if m['role'] == 'assistant']
        
        # Communication Mode - Shows whether you're in Chat or Call mode
        st.metric("Mode", mode_name, help="Current communication mode: Chat or Call")
        
        # Call Status - Only shown in Call mode, shows current call state
        if current_mode == 'call':
            call_status = st.session_state.call_status.get(st.session_state.selected_bot, 'idle')
            status_icon = {
                'idle': '📞',
                'ringing': '📞',
                'active': '✅',
                'ended': '📴'
            }.get(call_status, '📞')
            status_text = {
                'idle': 'Ready to call',
                'ringing': 'Connecting...',
                'active': 'Call in progress',
                'ended': 'Call ended'
            }.get(call_status, call_status.title())
            st.metric("Call Status", f"{status_icon} {status_text}", help="Current state of the call: Idle (ready), Ringing (connecting), Active (in progress), or Ended")
        
        # Message Statistics
        st.markdown("---")
        st.markdown("**Message Statistics:**")
        st.metric("Total Messages", len(messages), help="Total number of messages exchanged in this session")
        st.metric("User Messages", len(user_messages), help="Number of messages sent by you")
        st.metric("Bot Responses", len(bot_messages), help="Number of responses from the bot")
        
        # Feedback stats
        bot_feedback = st.session_state.feedback.get(st.session_state.selected_bot, {})
        session_fb = st.session_state.session_feedback.get(st.session_state.selected_bot)
        
        if bot_feedback:
            feedback_count = len(bot_feedback)
            avg_rating = sum(f['rating'] for f in bot_feedback.values()) / feedback_count if feedback_count > 0 else 0
            st.metric("Message Feedback", feedback_count)
            st.metric("Avg Message Rating", f"{avg_rating:.1f}/5")
        
        if session_fb:
            st.metric("Session Rating", f"⭐ {session_fb['rating']}/5")
        
        if not bot_feedback and not session_fb:
            st.info("No feedback yet")
        
        st.markdown("---")
        st.subheader("🔗 Vapi Status")
        config = st.session_state.api_configs[st.session_state.selected_bot]
        use_vapi = config.get('use_vapi', False)
        
        if use_vapi and config.get('assistant_id') and config.get('vapi_api_key'):
            st.success("✅ Vapi Active")
            st.caption(f"Assistant: {config.get('assistant_id', 'N/A')[:20]}...")
            if config.get('phone_number_id'):
                st.caption(f"Phone: {config.get('phone_number_id', 'N/A')[:20]}...")
        else:
            st.info("ℹ️ Vapi Not Configured")
            st.caption("Enable Vapi in Bot Settings")
    
    
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
            # Call mode - Vapi required
            st.markdown("---")
            st.warning("⚠️ **Vapi Required for Call Mode**")
            st.info("""
            To use Call mode, please configure Vapi:
            1. Go to **Bot Settings - Vapi** in the sidebar
            2. Enable Vapi for this bot
            3. Enter your Vapi API Key
            4. Enter your Assistant ID
            5. Save the configuration
            
            Once Vapi is configured, you'll be able to make voice calls with the bot.
            """)
    else:
        # Vapi handles input via its widget
        st.caption("💡 Use the Vapi widget above to interact with the bot")

if __name__ == "__main__":
    main()

