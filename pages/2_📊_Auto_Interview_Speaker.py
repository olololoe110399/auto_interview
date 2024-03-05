import os
import shutil

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from llm import GPTChatClient, Interviewer
from speech_recognition import save_wav_file, transcribe, text_to_speech_ai

# Set the page config
st.set_page_config(
    page_title="Auto Interview Speaker",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)

# Settings for the app
with st.sidebar.expander("Settings"):
    # Input for OpenAI API Key
    open_api_key = st.text_input(
        "OpenAI API Key:",
        key="open_api_key_2",
        # value="YOUR_API_KEY",
        value="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",
        type="password"
    )
    # Input for language
    language = st.selectbox(
        "Language:",
        key="language_2",
        options=["English", "Vietnamese"],
        index=0,
    )

    # Input for the number of questions
    how_many_questions = st.number_input(
        "How many questions would you like to ask?",
        key="how_many_questions_2",
        min_value=1,
        max_value=100,
        value=3,
    )

# Check if the OpenAI API Key is provided
if not open_api_key or not language or not how_many_questions:
    st.info("Please enter your settings", icon="🚨")
    st.stop()

st.sidebar.info("Please reload the page before update the settings.", icon="🚨")

# Set the OpenAI API Key
os.environ["OPENAI_API_KEY"] = open_api_key

st.header(":rocket: Technical Interview with AI :page_facing_up:")

# Input for the interview information
interviewing_for = st.text_input(
    "What position are you interviewing for?",
    key="interviewing_for_2",
    placeholder="Software Engineer",
    value="Flutter Developer",
)

# Input for the level of the position
level = st.text_input(
    "What level is the position?",
    key="level_2",
    placeholder="Senior",
    value="Middle",
)

# Input for the name of the candidate
name_of_candidate = st.text_input(
    "What is the name of the candidate?",
    key="name_of_candidate_2",
    placeholder="John Doe",
)

# Check if the interview information is provided
if not interviewing_for or not level or not how_many_questions or not name_of_candidate:
    st.info("Please enter the following information", icon="🚨")
    st.stop()

# Conduct the interview
if "interviewer_2" not in st.session_state:
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.makedirs('temp')
    # Clear the previous messages and interviewer
    st.session_state.pop("messages_2", None)
    st.session_state.pop("interviewer_2", None)
    # Create a new interviewer
    interview_category_determiner = GPTChatClient(json_mode=True, stream=False, hasPrint=False)
    # Ask the AI to determine the category of the interview
    interview_category_for_metrics = interview_category_determiner.ask_question(
        f"given a interviewing category return if it is 'code' or 'non-code'. Category: {interviewing_for}. "
        f"return your response as a JSON object as follows: {{'category': 'code'}} or {{'category': 'non-code'}}"
    )
    # Create a new interviewer
    st.session_state.interviewer_2 = Interviewer(
        interviewing_for=interviewing_for,
        level=level,
        name_of_candidate=name_of_candidate,
        how_many_questions=how_many_questions,
        category=interview_category_for_metrics['category'],
        enableUI=True,
        language=language,
    )
    # Add the first message to the AI
    st.session_state.interviewer_2.gpt_client.add_message(
        "system",
        f"Name of candidate: {st.session_state.interviewer_2.name_of_candidate}",
    )
    st.session_state.on_question_number_2 = 0

if "messages_2" not in st.session_state:
    st.session_state.messages_2 = []

# Display the messages
for message in st.session_state.messages_2:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["audio"]:
                st.audio(message["audio"])

# Chat with the AI
if "interviewer_2" in st.session_state:
    interviewer = st.session_state.interviewer_2
    # Check if the interview is over
    if st.session_state.on_question_number_2 > interviewer.how_many_questions:
        st.info("Interview is over. Please reload the page to start a new interview.", icon="🚨")
        st.stop()

    # Generate Getting Started message
    if st.session_state.on_question_number_2 == 0:
        with st.chat_message("assistant"):
            st.session_state.gpt_response_2 = st.session_state.interviewer_2.gpt_client.get_response()
            speech_file_path = f"temp/audio_response_{st.session_state.on_question_number_2}.mp3"
            text_to_speech_ai(speech_file_path, st.session_state.gpt_response_2)
            st.audio(speech_file_path)
            st.session_state.on_question_number_2 = 1
            st.session_state.messages_2.append(
                {
                    "role": "assistant",
                    "content": st.session_state.gpt_response_2,
                    "audio": speech_file_path,
                }
            )

    # Ask the next question
    if audio_input := audio_recorder(
        pause_threshold=2.5,
        sample_rate=44100,
        icon_size='1x',
    ):
        with st.chat_message("user"):
            wav_file_path = f"temp/audio_{st.session_state.on_question_number_2}.wav"
            save_wav_file(wav_file_path, audio_input)
            try:
                st.session_state.user_input_2 = transcribe(
                    audio_location=wav_file_path,
                    language="vi" if language == "Vietnamese" else "en"
                )
                st.markdown(st.session_state.user_input_2)
                st.audio(wav_file_path)
                st.session_state.messages_2.append(
                    {
                        "role": "user",
                        "content": st.session_state.user_input_2,
                        "audio": wav_file_path,
                    }
                )
            except Exception as e:
                print(e)
                st.error("Sorry, I did not catch that. Please try again.")
        with st.spinner("Processing..."):
            # Add the user input to the database
            interviewer.add_to_database({
                'question_number': st.session_state.on_question_number_2,
                'interviewing_for': interviewer.interviewing_for,
                'level': interviewer.level,
                'question': st.session_state.gpt_response_2,
                'answer': st.session_state.user_input_2,
                'evaluation': ''
            })
            # Notify the observer
            interviewer.notify_observer({
                "candidateName": interviewer.name_of_candidate,
                "input": st.session_state.gpt_response_2,
                "response": st.session_state.user_input_2,
                "question_number": st.session_state.on_question_number_2,
                "table_name": interviewer.table_name,
                "how_many_questions": interviewer.how_many_questions,
                "category": interviewer.category,
            })
        # If the last question was the final question
        if st.session_state.on_question_number_2 == interviewer.how_many_questions:
            with st.chat_message("assistant"):
                interviewer.gpt_client.add_message(
                    "system",
                    "last question was the final question. "
                    "Interview is over. "
                    "Please say goodbye to the candidate and end the interview.",
                )
                st.session_state.gpt_response_2 = interviewer.gpt_client.get_response()
                speech_file_path = f"temp/audio_response_{st.session_state.on_question_number_2}.mp3"
                text_to_speech_ai(speech_file_path, st.session_state.gpt_response_2)
                st.audio(speech_file_path)
                st.session_state.messages_2.append(
                    {
                        "role": "assistant",
                        "content": st.session_state.gpt_response_2,
                        "audio": speech_file_path,
                    }
                )
        else:
            # Generate the next question
            interviewer.gpt_client.add_message("user", st.session_state.user_input_2)
            with st.chat_message("assistant"):
                st.session_state.gpt_response_2 = interviewer.gpt_client.get_response()
                speech_file_path = f"temp/audio_response_{st.session_state.on_question_number_2}.mp3"
                text_to_speech_ai(speech_file_path, st.session_state.gpt_response_2)
                st.audio(speech_file_path)
                st.session_state.messages_2.append(
                    {
                        "role": "assistant",
                        "content": st.session_state.gpt_response_2,
                        "audio": speech_file_path,
                    }
                )

        st.session_state.on_question_number_2 += 1
