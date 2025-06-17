
import streamlit as st
import os
import io
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from streamlit_audio_recorder import audio_recorder
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if not api_key:
    st.error("❌ Error: GEMINI_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit page config
st.set_page_config(page_title="Adnan's AI Voice Assistant", page_icon="🎙️")
st.title("🎙️ Adnan's AI Voice Assistant")
st.markdown("Speak something and the AI will reply with voice!")

# Audio recording from browser
audio_bytes = audio_recorder(pause_threshold=2.0)

if audio_bytes:
    st.audio(audio_bytes, format='audio/wav')

    # Convert bytes to WAV for recognition
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
    audio.export("temp.wav", format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            user_text = recognizer.recognize_google(audio_data)
            st.markdown(f"**You said:** {user_text}")

            # Get AI response
            response = model.generate_content(user_text)
            reply_text = response.text.replace("Gemini", "AI")
            st.markdown(f"**AI says:** {reply_text}")

            # Convert reply to speech
            tts = gTTS(text=reply_text, lang='en')
            tts.save("reply.mp3")
            st.audio("reply.mp3", format="audio/mp3")

        except sr.UnknownValueError:
            st.error("Sorry, could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Speech recognition error: {e}")
