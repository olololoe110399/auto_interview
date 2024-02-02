from termcolor import colored

from llm import GPTChatClient, Interviewer


def main():
    print(colored("Welcome to the Interviewer!", "green"))
    print(colored("Please enter the following information:", "green"))
    interviewing_for = input(colored("What position are you interviewing for? ", "green"))
    level = input(colored("What level is the position? ", "green"))
    how_many_questions = int(input(colored("How many questions would you like to ask? ", "green")))
    name_of_candidate = input(colored("What is the name of the candidate? ", "green"))
    interview_category_determiner = GPTChatClient(json_mode=True, stream=False, hasPrint=False)
    interview_category_for_metrics = interview_category_determiner.ask_question(
        f"given a interviewing category return if it is 'code' or 'non-code'. Category: {interviewing_for}. "
        f"return your response as a JSON object as follows: {{'category': 'code'}} or {{'category': 'non-code'}}"
    )
    interviewer = Interviewer(
        interviewing_for=interviewing_for,
        level=level,
        name_of_candidate=name_of_candidate,
        how_many_questions=how_many_questions,
        category=interview_category_for_metrics['category'],
    )
    interviewer.conduct_interview()


if __name__ == "__main__":
    main()
