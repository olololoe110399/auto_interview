import os
import sqlite3

from llm.evaluator import Evaluator
from llm.gpt_chat_client import GPTChatClient
from llm.observable import Observable


# Create a new interviewer
class Interviewer(Observable):
    def __init__(
        self,
        interviewing_for="",
        level="",
        name_of_candidate="",
        how_many_questions=10,
        category="",
        enableUI=False,
        language="English",
    ):
        super().__init__()
        self.interviewing_for = interviewing_for
        self.level = level
        self.language = language
        self.how_many_questions = how_many_questions
        self.name_of_candidate = name_of_candidate
        self.category = category
        # Create a new Evaluator
        self.evaluator = Evaluator(category=self.category, language=self.language)
        # Register the Evaluator as an observer
        self.register_observer(self.evaluator)
        self.max_words_per_message = "100"
        # Create a new GPTChatClient
        self.gpt_client = GPTChatClient(enableUI=enableUI, max_words_per_message=self.max_words_per_message)
        # Set up the interview
        self.setup_interview()
        self.directory_of_this_script = os.path.dirname(os.path.realpath(__file__))
        # Connect to the database
        self.table_name = self.get_table_name()
        self.create_table()

    # Get the table name
    def get_table_name(self):
        base_name = self.name_of_candidate.replace(" ", "_")
        i = 1
        # Find a table name that doesn't exist
        with sqlite3.connect(os.path.join(self.directory_of_this_script, "interviews.db")) as conn:
            cursor = conn.cursor()
            while True:
                table_name = f"{base_name}_{i}" if i > 1 else base_name
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                # If the table doesn't exist, return the name
                if not cursor.fetchall():
                    return table_name
                i += 1

    # Create the table
    def create_table(self):
        with sqlite3.connect(os.path.join(self.directory_of_this_script, "interviews.db")) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                question_number TEXT NOT NULL,
                interviewing_for TEXT NOT NULL,
                level TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                evaluation TEXT
                )"""
            )
            conn.commit()

    # Set up the interview
    def setup_interview(self):
        system_message = f"""You are and export join interviewer for interviewing candidates on {self.interviewing_for}.
        Your role is to interact with the candidate, asking a series of questions to assess their skills and understanding in {self.interviewing_for}. 
        Make sure to be clear and supportive, providing guidance rarely and if needed. 
        Remember, your goal is to create a comfortable environment for the candidate to showcase their abilities.
        Start by greeting the candidate and progressively ask more difficult questions. 
        Always ask a questions unless the interview has ended. Never switch form being and interviewer. 
        You are interviewer until the end of the interview.
        Please use {self.max_words_per_message} words or less.
        Make sure {self.language} is the language you are using."""
        self.gpt_client.add_message("system", system_message)

    # Add the interview to the database
    def add_to_database(self, data):
        with sqlite3.connect(os.path.join(self.directory_of_this_script, "interviews.db")) as conn:
            cursor = conn.cursor()
            sql = f"""
            INSERT INTO {self.table_name} (question_number, interviewing_for, level, question, answer, evaluation)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                sql,
                (
                    data['question_number'],
                    data['interviewing_for'],
                    data['level'],
                    data['question'],
                    data['answer'],
                    data['evaluation'],
                ),
            )
            conn.commit()

    def conduct_interview(self):
        # Start the interview
        on_question_number = 1

        # Add the first message to the AI
        self.gpt_client.add_message("system", f"Name of candidate: {self.name_of_candidate}")
        # Generate Getting Started message
        gpt_response = self.gpt_client.get_response()

        # Ask the next question
        for _ in range(self.how_many_questions):
            # Add the user input to the database
            user_input = input("You:")
            self.add_to_database({
                'question_number': on_question_number,
                'interviewing_for': self.interviewing_for,
                'level': self.level,
                'question': gpt_response,
                'answer': user_input,
                'evaluation': ''
            })
            # Notify the observer
            self.notify_observer({
                "candidateName": self.name_of_candidate,
                "input": gpt_response,
                "response": user_input,
                "question_number": on_question_number,
                "table_name": self.table_name,
                "how_many_questions": self.how_many_questions,
                "category": self.category,
            })

            # Check if the interview is over
            if on_question_number == self.how_many_questions:
                # End the interview
                self.gpt_client.add_message(
                    "system",
                    "last question was the final question. "
                    "interview is over. please say goodbye to "
                    "the candidate and end the interview.",
                )
                # Get the AI response
                gpt_response = self.gpt_client.get_response()
                break
            # Get the AI response
            self.gpt_client.add_message("user", user_input)
            gpt_response = self.gpt_client.get_response()

            on_question_number += 1
