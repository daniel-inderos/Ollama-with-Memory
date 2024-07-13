# AI Chat Application with Structured Memory

## Description

This AI Chat Application is a Python-based interactive chatbot that uses a local AI model through Ollama. It features an autonomous memory system, allowing the AI to remember important information about the user across conversations. The AI is also time-aware, providing context-relevant responses based on the current date and time.

## Features

- Interactive chat interface in the terminal
- Autonomous memory system with structured data storage
- Time-aware responses
- Colored output for better readability
- Automatic notification when memory is updated

## Requirements

- Python 3.7+
- Ollama (with a compatible AI model, default is "llama3")
- Required Python packages:
  - ollama
  - colorama

## Installation

1. Clone this repository or download the script.
2. Install the required Python packages:
   ```
   pip install ollama colorama
   ```
3. Ensure Ollama is installed and set up on your system with the "llama3" model (or modify the `OLLAMA_MODEL` variable in the script to use a different model).

## Usage

1. Run the script:
   ```
   python main.py
   ```
2. Start chatting with the AI naturally.
3. The AI will automatically remember important information about you and use it in future conversations.
4. You'll see a "Memory Updated" message whenever the AI saves new information.
5. To exit the chat, type 'exit', 'quit', or 'bye'.

## Memory Structure

The AI stores information about the user in a structured JSON format, including categories such as:

- Personal information (name, gender, date of birth, etc.)
- Preferences
- Education
- Hobbies
- Achievements
- Challenges
- Social information
- Technology interests
- Travel experiences
- And more...

This structured approach allows for detailed and categorized memory storage, enabling more personalized interactions over time.

## Customization

You can customize the AI's behavior by modifying the `system_prompt` in the `chat_with_ai` function. This allows you to adjust how the AI interprets and stores information.

## Notes

- The AI's memory is stored in a local file named `user_info.json`. Ensure this file has appropriate read/write permissions.
- The AI uses the Ollama model specified by the `OLLAMA_MODEL` variable. Make sure you have this model available in your Ollama setup.

## Troubleshooting

If you encounter any issues:
1. Ensure all required packages are installed correctly.
2. Check that Ollama is properly set up with the specified model.
3. Verify that the script has permission to read/write the `user_info.json` file.

## Contributing

Contributions to improve the application are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.