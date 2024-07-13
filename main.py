import ollama
import json
import os
import re
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama for cross-platform colored output
init()

# Configuration
OLLAMA_MODEL = "gemma2"
USER_INFO_FILE = "user_info.json"

def colored_print(color, message):
    print(f"{color}{Style.BRIGHT}{message}{Style.RESET_ALL}")

def remove_trailing_commas(json_string):
    # Remove trailing commas from JSON string
    return re.sub(r',\s*}', '}', json_string)

def load_user_info():
    if os.path.exists(USER_INFO_FILE):
        try:
            with open(USER_INFO_FILE, 'r') as f:
                content = f.read()
                # Remove trailing commas before parsing
                cleaned_content = remove_trailing_commas(content)
                return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            colored_print(Fore.RED, f"Error reading user info file: {str(e)}")
            colored_print(Fore.YELLOW, "Contents of the file (after cleaning):")
            print(cleaned_content)
            colored_print(Fore.YELLOW, "Would you like to reset the user info? (y/n)")
            if input().lower() == 'y':
                return {}
            else:
                colored_print(Fore.RED, "Cannot proceed with corrupted user info. Exiting.")
                exit(1)
    return {}

def save_user_info(user_info):
    with open(USER_INFO_FILE, 'w') as f:
        json.dump(user_info, f, indent=2)

def update_user_info(user_info, new_info):
    def deep_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            elif isinstance(v, list):
                if k in d and isinstance(d[k], list):
                    d[k].extend([i for i in v if i not in d[k]])
                else:
                    d[k] = v
            else:
                d[k] = v
        return d

    user_info = deep_update(user_info, new_info)
    save_user_info(user_info)
    colored_print(Fore.YELLOW, "Memory Updated")
    return user_info

def parse_ai_response(response):
    parts = response.split("MEMORY_UPDATE:", 1)
    ai_message = parts[0].strip()
    memory_update = json.loads(parts[1]) if len(parts) > 1 else {}
    return ai_message, memory_update

def generate_ai_response(model, prompt, user_info):
    try:
        response = ollama.generate(model=model, prompt=prompt)
        ai_response = response['response'].strip()
        
        ai_message, memory_update = parse_ai_response(ai_response)
        
        if memory_update:
            user_info = update_user_info(user_info, memory_update)
        
        return ai_message, user_info
    except Exception as e:
        colored_print(Fore.RED, f"Error in generate_ai_response: {str(e)}")
        return "I apologize, but I encountered an error while processing your request.", user_info

def chat_with_ai(user_info):
    system_prompt = """
    You are an AI assistant capable of remembering important information about the user.
    When you learn something new and important about the user, you should save it to memory.
    To save information, include a JSON object at the end of your response like this:
    MEMORY_UPDATE: {{"key": "value"}}
    Only include the MEMORY_UPDATE if you have new information to save.
    Current user information: {user_info}
    Current date and time: {current_datetime}
    Use the current date and time to provide relevant responses and update memories with timestamps if appropriate.
    """
    
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = system_prompt.format(
            user_info=json.dumps(user_info, indent=2),
            current_datetime=current_datetime
        )
        prompt += f"\n\nUser: {user_input}\nAI:"
        ai_response, user_info = generate_ai_response(OLLAMA_MODEL, prompt, user_info)
        colored_print(Fore.CYAN, f"AI: {ai_response}")

def main():
    user_info = load_user_info()
    
    colored_print(Fore.CYAN, "Welcome to the AI Chat Application!")
    colored_print(Fore.CYAN, "Chat naturally with the AI. It will remember important information automatically.")
    colored_print(Fore.CYAN, "The AI is aware of the current date and time for context-aware responses.")
    colored_print(Fore.CYAN, "You'll be notified when the AI updates its memory about you.")
    colored_print(Fore.CYAN, "To exit, type 'exit', 'quit', or 'bye'.")

    if user_info:
        colored_print(Fore.MAGENTA, "I remember some things about you. Let's chat!")
    else:
        colored_print(Fore.MAGENTA, "I'm excited to learn about you. Let's start our conversation!")

    chat_with_ai(user_info)

if __name__ == "__main__":
    main()