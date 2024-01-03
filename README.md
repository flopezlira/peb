# Prompt Engineering Bot

## Description

Prompt Engineering Bot is an interactive Telegram bot designed to assist users in refining and enhancing prompts for AI models. Utilizing the Telegram API, it offers a streamlined, conversational interface for a better user experience.

It is based on the Prompt Engineering Canvas 

https://medium.com/@flopezlira/crafting-effective-ai-prompts-2f0decfb87a3
## Features

- Interactive stages for prompt development (goal setting, persona, task identification, etc.).
- Inline Telegram keyboard for easy navigation.
- OpenAI integration for prompt enhancement.
- Modular design for easy customization and expansion.

## Installation

To set up Prompt Engineering Bot, follow these steps:

1. **Clone the Repository**
git clone [repository URL]

2. **Install Dependencies**
- Ensure [Poetry](https://python-poetry.org/docs/) is installed on your system.
- Install the dependencies using Poetry:
  ```
  poetry install
  ```

3. **Environment Variables**
- Create a `.env` file in the root directory.
- Add the following variables 
    `TELEGRAM_TOKEN`
    `OPENAI_ORGANIZATION`
    `OPENAI_API_KEY`

## Running the Bot

To run the bot, use the following command:

poetry run python3 peb/telegram_bot.py

## Configuration

- **Telegram Bot Token**: Set your Telegram bot token in the `.env` file to connect the bot with the Telegram API.
- Do the same for openai tokens

## Contributing

Contributions are welcome. Please adhere to the project's code style and ensure all tests pass. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the **CC BY-NC** License

## Acknowledgments

- Thanks to OpenAI for the API powering prompt enhancements.

## Contact

For queries or suggestions, feel free to contact me at flopezlira@gmail.com.







