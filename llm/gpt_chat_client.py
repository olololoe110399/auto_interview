import json

import streamlit as st
from openai import OpenAI
from termcolor import colored


class GPTChatClient:
    def __init__(
        self,
        model="gpt-4-turbo-preview",
        max_history_words=5000,
        max_words_per_message="100",
        json_mode=False,
        stream=True,
        hasPrint=True,
        enableUI=False,
    ):
        self.container = None
        self.client = OpenAI()
        self.enableUI = enableUI
        self.model = model
        self.history = []
        self.hasPrint = hasPrint
        self.max_history_words = max_history_words
        self.max_words_per_message = max_words_per_message
        self.json_mode = json_mode
        self.stream = stream

    # Add a message to the history
    def add_message(self, role, content):
        if role == "user":
            self.history.append({
                "role": role,
                "content": content,
            })
        else:
            self.history.append({
                "role": role,
                "content": content,
            })

    # Clear the history
    def clear_history(self):
        self.history.clear()

    # Get the response from the AI
    def get_response(self):
        if self.enableUI:
            self.container = st.empty()
        if self.json_mode:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                stream=self.stream,
                response_format={"type": "json_object"},
            )
            if self.stream:
                assistant_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        text_chunk = chunk.choices[0].delta.content
                        if self.hasPrint:
                            print(colored(text_chunk, "yellow"), end="", flush=True)

                        assistant_response += str(text_chunk)
                        if self.enableUI:
                            self.container.markdown(assistant_response)

                assistant_response = json.loads(assistant_response)
            else:
                assistant_response = json.loads(response.choices[0].message.content)
                if self.hasPrint:
                    print(colored(assistant_response, "yellow"))
                if self.enableUI:
                    self.container.markdown(assistant_response)

        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                stream=self.stream,
            )
            if self.stream:
                assistant_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        text_chunk = chunk.choices[0].delta.content
                        if self.hasPrint:
                            print(colored(text_chunk, "yellow"), end="", flush=True)
                        assistant_response += str(text_chunk)
                        if self.enableUI:
                            self.container.markdown(assistant_response)
                if self.hasPrint:
                    print("\n")
            else:
                assistant_response = response.choices[0].message.content
                if self.hasPrint:
                    print(colored(assistant_response, "yellow"))
                if self.enableUI:
                    self.container.markdown(assistant_response)

        self.add_message("assistant", str(assistant_response))
        self._trim_history()
        return assistant_response

    def ask_question(self, question):
        self.add_message("user", question)
        return self.get_response()

    def _trim_history(self):
        words_count = sum(
            len(str(message["content"]).split()) for message in self.history
            if message["role"] != "system"
        )
        while words_count > self.max_history_words and len(self.history) > 1:
            words_count -= len(self.history[0]["content"].split())
            self.history.pop(1)


if __name__ == "__main__":
    gpt_client = GPTChatClient()
    gpt_client.add_message("system", "You are a helpful assistant.")
    print(gpt_client.ask_question("Who won the world cup in 2020?"))
    print(gpt_client.ask_question("Where was it played?"))
    print(gpt_client.history)
