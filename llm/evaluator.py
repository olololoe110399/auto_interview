import json
import os
import sqlite3
import threading

import pandas as pd
import streamlit as st
import yaml
from streamlit_gsheets import GSheetsConnection

from llm.gpt_chat_client import GPTChatClient


class Evaluator:
    def __init__(self, category, hasPrint=False, language="English"):
        self.conn_gg_sheet = None
        self.cursor = None
        self.conn = None
        # Create a new GPTChatClient
        self.gpt_client = GPTChatClient(
            stream=False,
            json_mode=True,
            max_words_per_message="200",
            model="gpt-4-turbo-preview",
            hasPrint=hasPrint,
        )
        self.language = language
        self.interview_metrics = "coding_interview_metrics" if category == "code" else "general_interview_metrics"
        self.directory_of_this_script = os.path.dirname(os.path.realpath(__file__))
        self.setup_evaluation()
        # Lock for the update database method
        self.lock = threading.Lock()

    # Add the evaluation to the database
    def add_to_database(self, question_number, evaluation, table_name):
        sql = f"""
        UPDATE {table_name}
        SET evaluation = ?  
        WHERE question_number = ?
        """
        self.cursor.execute(sql, (evaluation, question_number))
        self.conn.commit()
        data = self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        columns = ["question_number", "interviewing_for", "level", "question", "answer", "evaluation"]
        df = pd.DataFrame(data, columns=columns)

        def convert(x):
            try:
                return json.dumps(json.loads(x), ensure_ascii=False, indent=4)
            except:
                return x

        df['evaluation'] = df['evaluation'].apply(convert)
        self.add_to_gg_sheet(table_name, question_number, df)

    # Add the evaluation to the Google Sheet
    def add_to_gg_sheet(self, table_name, question_number, df):
        if question_number == 1:
            self.conn_gg_sheet.create(
                worksheet=table_name,
                data=df,
            )
        else:
            self.conn_gg_sheet.update(
                worksheet=table_name,
                data=df,
            )

    # Set up the evaluation
    def setup_evaluation(self):
        with open(os.path.join(self.directory_of_this_script, self.interview_metrics), 'r') as f:
            interview_metrics = f.read()
        system_message = f"""You are a job interview evaluator. You receive candidates' responses and evaluate them...
        After each answer that the candidate give, return a JSON object with the following format. 
        You only return the JSON object after getting a candidate's answer. Be very critical and meticulous in your evaluation.
        You have to update the scorecard considering previous scorecards that you have generated based on previous answers. 
        Make sure value of "reasoningForScoring" metric is a string and {self.language}.
        If you have no information on a evaluation metric just give it a score of 5. return your response as a JSON object as follows:
        {{
        "candidateName": "sting",
        "questionNumber": "integer",
        "evaluation": [
            {{
            {interview_metrics}
            "overallScore": "integer (1-10)" # make a weighted average of all the scores, give good reasons for the weights as we want to make this as objective as possible
            }}
        ],
        "evaluationCompleted": "boolean"
        }}"""
        self.gpt_client.add_message("system", system_message)

    def notify(self, data):
        self.conn = sqlite3.connect(os.path.join(self.directory_of_this_script, "interviews.db"))
        self.cursor = self.conn.cursor()
        self.conn_gg_sheet = st.connection("gsheets", type=GSheetsConnection)
        self.gpt_client.add_message(
            "user",
            f"Question to candidate: {data['input']}\nResponse from candidate: "
            f"{data['response']} .\nWe are on question number {data['question_number']}.\n"
            f"If we are on the last question please return 'evaluationCompeted': true",
        )
        gpt_response = self.gpt_client.get_response()

        # Save the scorecard
        with open(os.path.join(self.directory_of_this_script, "scorecard.yaml"), "w") as f:
            yaml.dump(gpt_response, f, allow_unicode=self.language == "Vietnamese")

        # Add the evaluation to the database
        with self.lock:
            self.add_to_database(
                question_number=data['question_number'],
                evaluation=json.dumps(gpt_response, ensure_ascii=self.language != "Vietnamese"),
                table_name=data['table_name']
            )
