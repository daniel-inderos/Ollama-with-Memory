import ollama
import json
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama for cross-platform colored output
init()

# Configuration
OLLAMA_MODEL = "llama3"
MEMORY_FILE = "user_memory.txt"

def colored_print(color, message):
    print(f"{color}{Style.BRIGHT}{message}{Style.RESET_ALL}")

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_memory(memories):
    with open(MEMORY_FILE, 'w') as f:
        f.write('\n'.join(memories))

def update_memory(memories, new_memory):
    memories.append(new_memory)
    save_memory(memories)
    colored_print(Fore.YELLOW, "Memory Updated")
    return memories

def remove_memory(memories, keyword):
    original_length = len(memories)
    memories = [m for m in memories if keyword.lower() not in m.lower()]
    if len(memories) < original_length:
        save_memory(memories)
        colored_print(Fore.YELLOW, "Memory Removed")
    return memories

def parse_ai_response(response):
    parts = response.split("MEMORY_UPDATE:", 1)
    ai_message = parts[0].strip()
    new_memory = parts[1].strip() if len(parts) > 1 else None
    
    remove_parts = ai_message.split("MEMORY_REMOVE:", 1)
    ai_message = remove_parts[0].strip()
    remove_keyword = remove_parts[1].strip() if len(remove_parts) > 1 else None
    
    return ai_message, new_memory, remove_keyword

def generate_ai_response(model, prompt, memories):
    try:
        response = ollama.generate(model=model, prompt=prompt)
        ai_response = response['response'].strip()
        
        ai_message, new_memory, remove_keyword = parse_ai_response(ai_response)
        
        if remove_keyword:
            memories = remove_memory(memories, remove_keyword)
        
        if new_memory:
            memories = update_memory(memories, new_memory)
        
        return ai_message, memories
    except Exception as e:
        colored_print(Fore.RED, f"Error in generate_ai_response: {str(e)}")
        return "I apologize, but I encountered an error while processing your request.", memories

def chat_with_ai(memories):
    system_prompt = """
    You are an AI assistant with a memory of important information about the user.
    Key points:
    1. Prioritize recent information in your responses.
    2. If the user mentions something new or exciting, focus on that in your reply.
    3. Use the stored memories to provide context-aware and personalized responses.
    4. If you're unsure about something, ask for clarification instead of making assumptions.
    5. To save a new memory, include it at the end of your response like this:
       MEMORY_UPDATE: [The new memory as a single sentence]
    6. Only include MEMORY_UPDATE if you have important new information to save.
    7. If the user asks you to forget specific information, include the keyword at the end of your response like this:
       MEMORY_REMOVE: [keyword]
    8. Do not include any tags like </start_of_turn> in your response.
    9. If the user gives an update on information, for example: weight, then remove the old piece of info and replace it with the new piece information.

    Current memories:
    {memories}

    Current date and time: {current_datetime}

    Respond naturally and engagingly, focusing on what the user is currently discussing.
    """
    
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = system_prompt.format(
            memories='\n'.join(memories),
            current_datetime=current_datetime
        )
        prompt += f"\n\nUser: {user_input}\nAI:"
        ai_response, memories = generate_ai_response(OLLAMA_MODEL, prompt, memories)
        colored_print(Fore.CYAN, f"AI: {ai_response}")

def main():
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