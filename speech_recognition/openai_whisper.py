import wave

import openai


class Config:
    channels = 2
    sample_width = 2
    sample_rate = 44100


def save_wav_file(file_path, wav_bytes):
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(Config.channels)
        wav_file.setsampwidth(Config.sample_width)
        wav_file.setframerate(Config.sample_rate)
        wav_file.writeframes(wav_bytes)


def transcribe(audio_location, language="English"):
    audio_file = open(audio_location, "rb")
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language
    )
    return transcript.text


def text_to_speech_ai(speech_file_path, api_response):
    response = openai.audio.speech.create(model="tts-1", voice="nova", input=api_response)
    response.stream_to_file(speech_file_path)


if __name__ == "__main__":
    import os

    os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
    try:
        user_input = transcribe("temp/audio.wav", language="vi")
        print(user_input)
    except Exception as e:
        print(e)
        print("Sorry, I did not catch that. Please try again.")
