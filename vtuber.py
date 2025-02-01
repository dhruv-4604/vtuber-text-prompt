"""
VTuber Text-to-Speech System
This module implements a simple text-to-speech converter using ElevenLabs.
"""

import streamlit as st
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(
    page_title="Quick TTS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize environment configuration
load_dotenv()

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Configure ElevenLabs client
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    st.error("Error: ELEVENLABS_API_KEY is not set in the environment variables.")
    st.stop()

@st.cache_resource
def get_tts_client():
    return ElevenLabs(api_key=ELEVENLABS_API_KEY)

ttsClient = get_tts_client()

@lru_cache(maxsize=100)
def get_cached_audio(text):
    return ttsClient.text_to_speech.convert(
        text=text,
        voice_id="vGQNBgLaiM3EdZtxIiuY",
        output_format="mp3_44100_128",
        model_id="eleven_multilingual_v2",
    )

def text_to_speech(text):
    """
    Converts text to speech using ElevenLabs API and streams the audio output.
    """
    try:
        if len(text) <= 100:
            audio_stream = get_cached_audio(text)
        else:
            audio_stream = ttsClient.text_to_speech.convert(
                text=text,
                voice_id="vGQNBgLaiM3EdZtxIiuY",
                output_format="mp3_44100_128",
                model_id="eleven_multilingual_v2",
            )
        stream(audio_stream)
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.history.insert(0, {"text": text, "time": timestamp})
    except Exception as e:
        st.error(f"Error in TTS: {e}")

def handle_input():
    if st.session_state.user_input:
        text_to_speech(st.session_state.user_input)
        st.session_state.user_input = ""

# Use custom CSS to make the interface more responsive
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        font-size: 20px;
    }
    .history-item {
        padding: 8px 12px;
        margin: 4px 0;
        background-color: #f0f2f6;
        border-radius: 4px;
    }
    .history-time {
        color: #666;
        font-size: 12px;
    }
    .history-text {
        color: #1f1f1f;
        font-size: 14px;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Quick Text to Speech")

# Single text input
st.text_input(
    "",
    placeholder="Enter your message here and press Enter...",
    key="user_input",
    on_change=handle_input
)

# Display history in a simple format
if st.session_state.history:
    st.markdown("### Message History")
    for item in st.session_state.history:
        st.markdown(f"""
            <div class="history-item">
                <div class="history-time">{item['time']}</div>
                <div class="history-text">{item['text']}</div>
            </div>
        """, unsafe_allow_html=True)