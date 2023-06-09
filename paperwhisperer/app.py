from os import path
from dotenv import load_dotenv
from openai import ChatCompletion
from streamlit_chat import message
import streamlit as st
from typing import List

# Set enviornment variables
load_dotenv()

# Set helper functions
def prepare_context() -> str:
    """
    Prepare the AI model's context.

    Returns:
        A string representing the context for the AI model.
    """

    # __file__ is a built-in variable in Python, which is the path of the
    # current script file
    current_script_path = path.realpath(__file__)

    # This will give you the directory of the current script
    current_script_directory = path.dirname(current_script_path)

    # This constructs the path of the file you want to read, relative to the
    # current script
    file_path = path.join(current_script_directory, 'how_to_read_a_paper.txt')

    # Read in paper to help AI structure paper reviews
    with open(file_path, 'r') as file:
        how_to_text = file.read()

    # Set context for ChatCompletion
    context = f"""You are a helpful assistant that assists users in reviewing 
    and learning from papers. Please read the following paper in the pair of 
    triple equal signs. After you're done, please use that paper for guiding 
    the user in understanding in the papers the user submits.

    ===
    {how_to_text}
    === 
    """

    return context

def generate_response(prompt: str) -> None:
    """
    Generate a response from the AI model based on the user's prompt.

    Args:
        prompt: A string containing the user's input.

    This function does not return any value. It updates the 'messages' attribute
      of the Streamlit session state.
    """
    # Add the user's prompt to the messages
    st.session_state['messages'].append({"role": "user", "content": prompt})

    # Generate the chat completion
    chat_completion = ChatCompletion.create(
        model='gpt-4',
        messages=st.session_state['messages']
    )
    # Extract the response from the chat completion
    response = chat_completion.choices[0].message.content

    # Add the generated response to the messages
    st.session_state['messages'].append(
        {"role": "assistant", "content": response})


def update_chat_state(role: str) -> List[str]:
    """
    Update the chat state based on the type of state.

    Args:
        role: A string that can be 'user' or 'assistant'.

    Returns:
        A list of strings, each string representing a message of the 
        corresponding role.
    """
    return [msg['content'] for msg in st.session_state['messages']
            if msg['role'] == role]


def display_chat_history() -> None:
    """
    Display the chat history in the Streamlit app.

    This function does not return any value. It adds messages to the Streamlit 
    UI.
    """
    if st.session_state['generated']:
        # Display the generated and past messages in reverse order
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            # Display the generated message
            message(st.session_state["generated"][i], key=str(i))
            # Display the past message
            message(st.session_state['past'][i], is_user=True,
                    key=str(i) + '_user')
            
def get_prompt():
    input_text = st.text_input("You: ", key="input")
    return input_text


def main() -> None:
    """
    The main function that runs the Streamlit app.

    This function does not return any value. It initializes the state, handles 
    user input, generates responses, updates the chat state, and displays the 
    chat history.
    """
    # Set the page configuration
    st.set_page_config(
        page_title="GPT4 32k Chat",
        page_icon="🤖"
    )

    # Set the page header
    st.header("GPT4 32k Chat")

    # Initialize the state if it hasn't been initialized yet
    if 'messages' not in st.session_state:
        # Prepare the context for the AI model
        context = prepare_context()
        st.session_state['messages'] = [
            {"role": "system", "content": context}
        ]

    # Initialize the generated messages if they haven't been initialized yet
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    # Initialize the past messages if they haven't been initialized yet
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    # Get user input
    prompt = get_prompt()

    if prompt:
        # Generate a response
        generate_response(prompt)

        # Update the chat state
        st.session_state['past'] = update_chat_state(role='user')
        st.session_state['generated'] = update_chat_state(role='assistant')

        # Display the updated chat history
        display_chat_history()


if __name__ == "__main__":
    main()
