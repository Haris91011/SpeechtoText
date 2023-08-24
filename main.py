import streamlit as st
import os
import openai
import numpy as np
import pathlib
from elevenlabs import generate, play,save 
import wave
from elevenlabs import set_api_key
from dotenv import load_dotenv
from pathlib import Path
import pyaudio
import config       

# openapi_key = config.openai.api_key
# eleven_lab = config.elevenlabs.api_key


load_dotenv()
# eleven_lab = os.getenv("ELEVENLAB")
# openapi_key = os.getenv("OPENAPI")
openapi_key = st.secrets["open_ai_key"]
eleven_lab = st.secrets["elevenlabs_key"]

set_api_key(eleven_lab)
openai.api_key = openapi_key
os.environ["OPENAI_API_KEY"] = openapi_key

st.markdown("<h1 style='text-align: center; color: green;'>Virtual Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: lightgreen; font-size: smaller;'>Get expert medical advice and diagnosis from the comfort with our Virtual General Physician service.</h2>", unsafe_allow_html=True)



st.title("Text to speech")
text = st.text_input("Enter text")
speaker = st.selectbox(
    "Select Speaker Gender",
    (
        "Male",
        "Female"
    ),
)

if speaker == "Male":
    speaker_name = "Antoni"
elif speaker == "Female":
    speaker_name = "Domi"


def tts(user_query: str):
    try:
        text = user_query
        audio = generate(
            text=text,
            voice=f'{speaker_name}',
            model='eleven_multilingual_v1'
        )
        filepath = "front_end1.mp3"
        root_dir = pathlib.Path.cwd()
        filepath = root_dir / Path('try.mp3')
        save(audio, filepath)
        return filepath
    except Exception as e:
        st.warning("Elevenlab API Key Error. Change your key.")

with st.spinner():
    if st.button("convert"):
        filepath = tts( text)
        try:
            audio_file = open(str(filepath), "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Your audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        except Exception as e:
            st.warning("Failed to upload the audio")


st.title("Speech to Text")
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 10


if st.button("Record"):
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
    except Exception as e:
        st.warning("Can't able to record your audio")

    st.write("Done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    root_dir = pathlib.Path.cwd()
    filename = root_dir / Path('try1.mp3')
    with wave.open(str(filename), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


    audio_file = open(str(filename), "rb")
    with st.spinner('Transcribing audio...'):
        try:
            transcribed_text = openai.Audio.transcribe("whisper-1", audio_file)
            st.success(str(transcribed_text['text']))
        except Exception as e:
            print(e)
            st.warning("OpenAI API key Error. Replace your key.")
