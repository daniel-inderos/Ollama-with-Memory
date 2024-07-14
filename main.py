import ollama
import json
from colorama import init, Fore, Style
from datetime import datetime, timedelta
import logging
from typing import List, Tuple
import re

# Initialize colorama for cross-platform colored output
init()

# Configuration
OLLAMA_MODEL = "llama3"
MEMORY_FILE = "user_memory.txt"
LOG_FILE = "ai_chat.log"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def colored_print(color: str, message: str) -> None:
    print(f"{color}{Style.BRIGHT}{message}{Style.RESET_ALL}")

def load_memory() -> List[str]:
    try:
        with open(MEMORY_FILE, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        logging.warning(f"Memory file not found: {MEMORY_FILE}")
        return []

def save_memory(memories: List[str]) -> None:
    with open(MEMORY_FILE, 'w') as f:
        f.write('\n'.join(memories))

def update_memory(memories: List[str], new_memory: str) -> List[str]:
    memories.append(new_memory)
    save_memory(memories)
    colored_print(Fore.YELLOW, "Memory Updated")
    logging.info(f"Memory updated: {new_memory}")
    return memories

def remove_memory(memories: List[str], keyword: str) -> List[str]:
    original_length = len(memories)
    memories = [m for m in memories if keyword.lower() not in m.lower()]
    if len(memories) < original_length:
        save_memory(memories)
        colored_print(Fore.YELLOW, "Memory Removed")
        logging.info(f"Memory removed with keyword: {keyword}")
    return memories

def calculate_actual_date(relative_date: str, current_date: datetime) -> str:
    relative_date = relative_date.lower()
    if 'tomorrow' in relative_date:
        return (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'next week' in relative_date:
        return (current_date + timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif 'in two days' in relative_date:
        return (current_date + timedelta(days=2)).strftime('%Y-%m-%d')
    elif 'in a week' in relative_date:
        return (current_date + timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif 'next month' in relative_date:
        return (current_date + timedelta(days=30)).strftime('%Y-%m-%d')  # Approximation
    else:
        return current_date.strftime('%Y-%m-%d')  # Default to current date if unrecognized

def parse_ai_response(response: str, current_date: datetime) -> Tuple[str, str, str]:
    parts = response.split("MEMORY_UPDATE:", 1)
    ai_message = parts[0].strip()
    new_memory = parts[1].strip() if len(parts) > 1 else None
    
    remove_parts = ai_message.split("MEMORY_REMOVE:", 1)
    ai_message = remove_parts[0].strip()
    remove_keyword = remove_parts[1].strip() if len(remove_parts) > 1 else None
    
    if new_memory:
        # Extract only the first sentence of the memory update
        new_memory = re.split(r'(?<=[.!?])\s', new_memory)[0]
        
        # Check if the new memory contains a relative date and update it
        date_pattern = r'\b(tomorrow|next week|in two days|in a week|next month)\b'
        matches = re.findall(date_pattern, new_memory, re.IGNORECASE)
        for match in matches:
            actual_date = calculate_actual_date(match, current_date)
            new_memory = re.sub(r'\b' + re.escape(match) + r'\b', actual_date, new_memory, flags=re.IGNORECASE)
        
        # Remove any remaining placeholders
        new_memory = re.sub(r'\[calculated date, e\.g\.,.*?\]', '', new_memory).strip()
    
    return ai_message, new_memory, remove_keyword

def generate_ai_response(model: str, prompt: str, memories: List[str], current_date: datetime) -> Tuple[str, List[str]]:
    try:
        response = ollama.generate(model=model, prompt=prompt)
        ai_response = response['response'].strip()
        
        ai_message, new_memory, remove_keyword = parse_ai_response(ai_response, current_date)
        
        if remove_keyword:
            memories = remove_memory(memories, remove_keyword)
        
        if new_memory:
            memories = update_memory(memories, new_memory)
        
        return ai_message, memories
    except Exception as e:
        error_msg = f"Error in generate_ai_response: {str(e)}"
        colored_print(Fore.RED, error_msg)
        logging.error(error_msg)
        return "I apologize, but I encountered an error while processing your request.", memories

def chat_with_ai(memories: List[str]) -> None:
    system_prompt = """
    You are an AI assistant with a memory of important information about the user. Your primary goal is to provide personalized and context-aware responses based on this memory.

    Instructions:
    1. Always reference and use the stored memories to personalize your replies. If a memory is relevant to the current conversation, explicitly mention it.
    2. If you're unsure about something or need more information, ask for clarification. Do not make assumptions.
    3. After each of your responses, assess if you've learned any important new information about the user. If so, add a new memory using this format:
       MEMORY_UPDATE: [New memory as a single, concise sentence]
    4. If the user asks you to forget specific information, acknowledge this and include the following at the end of your response:
       MEMORY_REMOVE: [Specific keyword or phrase to be removed]
    5. If the user provides information that updates or contradicts an existing memory, update it by removing the old information and adding the new one.
    6. Do not use any XML-like tags (e.g., </start_of_turn>) in your responses.
    7. Always be aware of the current date and time provided, and use this information to give timely and relevant responses.
    8. When the user mentions a relative date (e.g., "tomorrow," "next week," "in two days"), evaluate if the event or information associated with this date is important. If it is, include the relative date term in the memory update. The system will automatically convert it to an actual date. For example:
       User: "I have an important presentation tomorrow."
       You: "I understand you have an important presentation tomorrow. I'll make a note of that."
       MEMORY_UPDATE: User has an important presentation tomorrow.
    9. Keep memory updates brief and focused on the key information. Do not include additional conversational text or questions in the MEMORY_UPDATE.

    Current user memories:
    {memories}

    Current date and time: {current_datetime}

    Respond naturally and engagingly, focusing on the current topic of discussion while leveraging past information when relevant. Your responses should clearly demonstrate the use of memories and adherence to these instructions.
    """
    
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break

        current_datetime = datetime.now()
        prompt = system_prompt.format(
            memories='\n'.join(memories),
            current_datetime=current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        )
        prompt += f"\n\nUser: {user_input}\nAI:"
        ai_response, memories = generate_ai_response(OLLAMA_MODEL, prompt, memories, current_datetime)
        colored_print(Fore.CYAN, f"AI: {ai_response}")

def main() -> None:
    memories = load_memory()
    
    colored_print(Fore.CYAN, "Welcome to the AI Chat Application!")
    colored_print(Fore.CYAN, "Chat naturally with the AI. It will remember important information automatically.")
    colored_print(Fore.CYAN, "The AI is aware of the current date and time for context-aware responses.")
    colored_print(Fore.CYAN, "You can ask the AI to forget specific information if needed.")
    colored_print(Fore.CYAN, "To exit, type 'exit', 'quit', or 'bye'.")

    if memories:
        colored_print(Fore.MAGENTA, "I remember some things about you. Let's chat!")
    else:
        colored_print(Fore.MAGENTA, "I'm excited to learn about you. Let's start our conversation!")

    chat_with_ai(memories)

if __name__ == "__main__":
    main()