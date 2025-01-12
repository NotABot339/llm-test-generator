from agent import Agent
import logging
from agents import assistant_agent
from tools import test_files_in_folder, test_single_file


# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )

# test_files_in_folder()

print("Assistant: How can i help you?")
while True:
    user_input = input("User: ")
    if user_input.lower() == 'exit':
        print("Exiting the agent...")
        break
    
    assistant_agent.add_custom_tools({
        test_files_in_folder.__name__: test_files_in_folder,
        test_single_file.__name__: test_single_file
    })
    assistant_agent.add_message(user_input)
    answer = assistant_agent.run_agent()
    print(f"Assistant: {answer}")