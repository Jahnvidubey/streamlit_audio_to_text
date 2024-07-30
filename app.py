import streamlit as st
import os
import tempfile
import whisper
from utils import convert_to_abbreviation

# Load Whisper model
model = whisper.load_model("base")

# Function to transcribe audio
def transcribe_audio(file):
    audio_bytes = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
        tmp_audio_file.write(audio_bytes)
        tmp_audio_file.seek(0)
        result = model.transcribe(tmp_audio_file.name)
    return result["text"]

# Set up temporary directory for storing transcriptions
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = tempfile.TemporaryDirectory()

# Initialize a flag to keep track of whether files need to be cleared
if "clear_files" not in st.session_state:
    st.session_state.clear_files = False

def clear_temp_files():
    st.session_state.temp_dir.cleanup()
    st.session_state.temp_dir = tempfile.TemporaryDirectory()
    st.session_state.clear_files = False

# UI Components
st.title("Audio to Text Converter using Whisper Model")

uploaded_files = st.file_uploader("Upload audio files", type=["mp3", "wav", "m4a"], accept_multiple_files=True)

if st.button("Transcribe All"):
    if uploaded_files:
        if st.session_state.clear_files:
            clear_temp_files()
        with st.spinner('Transcribing files, please wait...'):
            for uploaded_file in uploaded_files:
                file_path = os.path.join(st.session_state.temp_dir.name, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                transcription = transcribe_audio(uploaded_file)
                transcription = convert_to_abbreviation(transcription)
                transcription_file_path = file_path.replace(".mp3", ".txt").replace(".wav", ".txt").replace(".m4a", ".txt")
                with open(transcription_file_path, "w") as f:
                    f.write(transcription)
            st.session_state.clear_files = True
            st.success("Transcription completed!")

if st.session_state.clear_files and uploaded_files:
    for uploaded_file in uploaded_files:
        text_file_name = uploaded_file.name.replace(".mp3", ".txt").replace(".wav", ".txt").replace(".m4a", ".txt")
        text_file_path = os.path.join(st.session_state.temp_dir.name, text_file_name)
        if os.path.exists(text_file_path):
            with open(text_file_path, "r") as f:
                transcription = f.read()
            st.download_button(
                label=f"Download {text_file_name}",
                data=transcription,
                file_name=text_file_name,
                mime="text/plain",
                key=text_file_name
            )
