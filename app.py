import os

import streamlit as st

from llm import GPTChatClient, Interviewer

# Settings for the app
with st.sidebar.expander("Settings", expanded=True):
    # Input for OpenAI API Key
    open_api_key = st.text_input(
        "OpenAI API Key:",
        key="open_api_key",
        value="YOUR_API_KEY",
        type="password"
    )
    # Input for language
    language = st.selectbox(
        "Language:",
        key="language",
        options=["English", "Vietnamese"],
        index=0,
    )

# Check if the OpenAI API Key is provided
if not open_api_key:
    st.info("Please enter your OpenAI API Key", icon="🚨")
    st.stop()

# Set the OpenAI API Key
os.environ["OPENAI_API_KEY"] = open_api_key

st.header(":rocket: Interview with AI :page_facing_up:")

st.sidebar.info("Please reload the page before update the settings.", icon="🚨")

# Input for the interview information
interviewing_for = st.text_input(
    "What position are you interviewing for?",
    key="interviewing_for",
    placeholder="Software Engineer",
    value="Flutter Developer",
)

# Input for the level of the position
level = st.text_input(
    "What level is the position?",
    key="level",
    placeholder="Senior",
    value="Middle",
)

# Input for the number of questions
how_many_questions = st.number_input(
    "How many questions would you like to ask?",
    key="how_many_questions",
    min_value=1,
    max_value=100,
    value=3,
)

# Input for the name of the candidate
name_of_candidate = st.text_input(
    "What is the name of the candidate?",
    key="name_of_candidate",
    placeholder="John Doe",
    value="Duy",
)

# Check if the interview information is provided
if not interviewing_for or not level or not how_many_questions or not name_of_candidate:
    st.info("Please enter the following information", icon="🚨")
    st.stop()

# Conduct the interview
if st.button("Conduct interview"):
    # Clear the previous messages and interviewer
    st.session_state.pop("messages", None)
    st.session_state.pop("interviewer", None)
    # Create a new interviewer
    interview_category_determiner = GPTChatClient(json_mode=True, stream=False, hasPrint=False)
    # Ask the AI to determine the category of the interview
    interview_category_for_metrics = interview_category_determiner.ask_question(
        f"given a interviewing category return if it is 'code' or 'non-code'. Category: {interviewing_for}. "
        f"return your response as a JSON object as follows: {{'category': 'code'}} or {{'category': 'non-code'}}"
    )
    # Create a new interviewer
    st.session_state.interviewer = Interviewer(
        interviewing_for=interviewing_for,
        level=level,
        name_of_candidate=name_of_candidate,
        how_many_questions=how_many_questions,
        category=interview_category_for_metrics['category'],
        enableUI=True,
        language=language,
    )
    # Add the first message to the AI
    st.session_state.interviewer.gpt_client.add_message(
        "system",
        f"Name of candidate: {st.session_state.interviewer.name_of_candidate}",
    )
    st.session_state.on_question_number = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat with the AI
if "interviewer" in st.session_state:
    interviewer = st.session_state.interviewer
    # Check if the interview is over
    if st.session_state.on_question_number > how_many_questions:
        st.info("Interview is over. Please reload the page to start a new interview.", icon="🚨")
        st.stop()

    # Generate Getting Started message
    if st.session_state.on_question_number == 0:
        with st.chat_message("assistant"):
            st.session_state.gpt_response = st.session_state.interviewer.gpt_client.get_response()
            st.session_state.on_question_number = 1
            st.session_state.messages = st.session_state.interviewer.gpt_client.history

    # Ask the next question
    if user_input := st.chat_input("Enter your answer here:"):
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Processing..."):
            # Add the user input to the database
            interviewer.add_to_database({
                'question_number': st.session_state.on_question_number,
                'interviewing_for': interviewer.interviewing_for,
                'level': interviewer.level,
                'question': st.session_state.gpt_response,
                'answer': user_input,
                'evaluation': ''
            })
            # Notify the observer
            interviewer.notify_observer({
                "candidateName": interviewer.name_of_candidate,
                "input": st.session_state.gpt_response,
                "response": user_input,
                "question_number": st.session_state.on_question_number,
                "table_name": interviewer.table_name,
                "how_many_questions": interviewer.how_many_questions,
                "category": interviewer.category,
            })
        # If the last question was the final question
        if st.session_state.on_question_number == interviewer.how_many_questions:
            with st.chat_message("assistant"):
                interviewer.gpt_client.add_message(
                    "system",
                    "last question was the final question. "
                    "Interview is over. "
                    "Please say goodbye to the candidate and end the interview.",
                )
                st.session_state.gpt_response = interviewer.gpt_client.get_response()
        else:
            # Generate the next question
            interviewer.gpt_client.add_message("user", user_input)
            with st.chat_message("assistant"):
                st.session_state.gpt_response = interviewer.gpt_client.get_response()

        st.session_state.on_question_number += 1
        st.session_state.messages = interviewer.gpt_client.history
