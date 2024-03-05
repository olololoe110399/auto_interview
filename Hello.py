import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Auto Interviewer! 👋")

st.sidebar.success("Select a interview round above.")

st.markdown(
    """
    Auto Interviewer is a self-sustaining interview agent that conducts interviews, 
    evaluates candidates, and updates a SQLite database and Google Sheets concurrently. 
    It utilizes threading, a queue system, and an observer pattern for efficient 
    parallelization and automatic notification of evaluators.
    
    **👈 Select a interview round from the sidebar** to see some examples
    of what Auto Interviewer can do!
    ### Code files and video for this project
    - Check out [youtube](https://www.youtube.com/watch?v=LLFkEv4dMiU)
    - Source code [github](https://github.com/olololoe110399/auto_interview)
    - Interviews [google sheet](https://docs.google.com/spreadsheets/d/1bFwQc55UwS2axNfwHvA4D0Q0NKi1SO2JisHRdZczqgQ/edit#gid=982202145)
"""
)
