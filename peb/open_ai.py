import logging
import os

import openai
from dotenv import load_dotenv

load_dotenv()
openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class OpenAI:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.5
        self.VALIDATION_PROMPT = (
            "I am going to give you a prompt enclosed within angle brackets <> for your "
            "analysis. Do not answer it. Your task is just to make sure that it does not contain"
            " personal or confidential information, that it does not seek to engage in harmful "
            " or illegal"
            " activities, that it does not seek to generate misinformation or disinformation, "
            " that it does not"
            " include discrimination, harassment or hate speech, that it does not request "
            " assistance in"
            " deceiving or manipulating anyone, and that it does not ask for specific medical or "
            " legal"
            ' diagnoses. If the prompt does not violate any rules, just say "Ok". If the prompt '
            " breaks any"
            ' rules, just say "No". Do not say anything else'
        )

        self.PROMPT_ENHANCEMENT_INSTRUCTION = """Your objective is to refine a draft prompt provided by the user. 
        Your task is to optimize the prompt for clarity, completeness, and effectiveness, ensuring that it is 
        perfectly understandable by ChatGPT. If the draft prompt lacks essential information, your role is to fill in 
        the gaps appropriately. The final output should be a single paragraph, not exceeding 500 words, and formatted 
        in plain text. The audience for the enhanced prompt is ChatGPT itself, so the language should be tailored to 
        what the model can understand best. Please adhere strictly to these guidelines to ensure the highest quality 
        output. Don't answer the question directly. Your task is to generate a prompt that ChatGPT can use to answer 
        the question. Think step by step. The draft prompt will be enclosed within angle brackets <>."""

    def create(self, instruction, prompt, enhancement=None):
        # if enhancement:
        #     self.PROMPT_ENHANCEMENT_INSTRUCTION += enhancement
        logger.info("Instruction: %s", instruction)
        response = openai.ChatCompletion.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": "<" + prompt + ">"},
                {"role": "system", "content": enhancement},
            ],
        )
        return response

    def moderate(self, prompt):
        logger.info("Moderating: %s", prompt)
        response = openai.Moderation.create(input=prompt)
        logger.info("Moderation response: %s", response)
        return response["results"][0]["flagged"]


if __name__ == "__main__":
    connection = OpenAI()
