import base64

import requests

url = "https://a2ec-34-32-210-42.ngrok-free.app/"

import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

with open('temp/audio_response_0.mp3', 'rb') as f:
    audio_bytes = f.read()

with open('temp/avatar.png', 'rb') as f:
    image_bytes = f.read()

if audio_bytes and image_bytes:
    image64 = base64.b64encode(image_bytes).decode()
    audio64 = base64.b64encode(audio_bytes).decode()
    # set timeout

    response = requests.post(
        url,
        json={"audio": audio64, "image": image64},
        timeout=9999,
    )
    video64 = response.json()['video']
    video_bytes = base64.b64decode(video64)
    st.video(video_bytes, start_time=0)
    with open('temp/response.mp4', 'wb') as f:
        f.write(video_bytes)
