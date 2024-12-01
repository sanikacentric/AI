import streamlit as st 
import openai
import tempfile
import os
from openai import OpenAI
import time  # Importing time module for sleep functionality
from dotenv import load_dotenv  # Importing load_dotenv
import logging
import openai
import os
import logging

# Initialize the OpenAI API client
client = openai

# =============================
# Configuration and Initialization
# =============================

# Load environment variables from .env file (if using one)
load_dotenv()

# Setup Logging
logging.basicConfig(
    filename='app.log',
    filemode='a',  # Append to existing log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    logger.error("OpenAI API key not found in environment variables.")
    st.stop()

openai.api_key = openai_api_key
client = openai  # Update this if your SDK uses a different method

# =============================
# Helper Functions
# =============================

def initialize_session_state():
    """Initialize session state variables."""
    if 'data_analysis_assistant_id' not in st.session_state:
        st.session_state.data_analysis_assistant_id = None
    if 'chat_assistant_id' not in st.session_state:
        st.session_state.chat_assistant_id = None
    # Initialize query_params in session_state if not already initialized
    if 'query_params' not in st.session_state:
        st.session_state.query_params = {}

def create_assistant(instructions, model="gpt-4", tools=None, tool_resources=None):
    """Create an assistant and store its ID in session state."""
    try:
        assistant = client.beta.assistants.create(
            instructions=instructions,
            model=model,
            tools=tools or [],
            tool_resources=tool_resources or {}
        )
        logger.info(f"Assistant created with ID: {assistant['id']}")
        return assistant["id"]
    except Exception as e:
        logger.error(f"Failed to create assistant: {e}")
        st.error(f"Failed to create assistant: {e}")
        return None

def run_assistant(assistant_id, instructions, tools=None):
    """Run the assistant with given instructions."""
    try:
        response = client.beta.assistants.run(
            assistant_id=assistant_id,
            instructions=instructions,
            tools=tools or {}
        )
        logger.info(f"Assistant {assistant_id} ran successfully.")
        return response["result"]
    except Exception as e:
        logger.error(f"Failed to run assistant {assistant_id}: {e}")
        st.error(f"Failed to run assistant: {e}")
        return None

# =============================
# Data Analysis Assistant
# =============================


# ================================
# Data Analysis Assistant Function
# ================================
def data_analysis_assistant():
    st.title("Data Analysis Assistant")
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

    if uploaded_file is not None:
        try:
            file_data = uploaded_file.read()
            file_name = uploaded_file.name

            # Handle file upload securely with tempfile
            with tempfile.NamedTemporaryFile(delete=True, suffix=".csv") as tmp:
                tmp.write(file_data)
                tmp.seek(0)

                # Upload the file to OpenAI with the purpose 'assistants'
                file = client.files.create(
                    file=open(tmp.name, "rb"),
                    purpose='assistants'
                )
                
            st.success(f"File '{file_name}' uploaded successfully with ID: {file.id}")
            st.write(f"File ID: {file.id}")

            # Create an assistant with the uploaded file and enable Code Interpreter
            assistant = client.beta.assistants.create(
                instructions="You are a data analyst. Please write and execute code to analyze the uploaded CSV file and provide insights.",
                model="gpt-4o",  # Replace with your required model
                tools=[{"type": "code_interpreter"}],
                tool_resources={
                    "code_interpreter": {
                        "file_ids": [file.id]
                    }
                }
            )
            
            st.success(f"Assistant created successfully with ID: {assistant.id}")
            st.write(f"Assistant ID: {assistant.id}")

            # Create a thread and pass the file as part of the message creation request
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Please write and execute code to analyze the uploaded CSV file and provide insights.",
                        "attachments": [
                            {
                                "file_id": file.id,
                                "tools": [{"type": "code_interpreter"}]
                            }
                        ]
                    }
                ]
            )
            st.success(f"Thread created successfully with ID: {thread.id}")
            st.write(f"Thread Response: {thread}")  # Log the full thread response for inspection

            # Polling or waiting for the assistant's message response
            if st.button("Analyze Data"):
                max_retries = 20  # Increased from 10 to 20
                retry_count = 0
                message_found = False

                # Poll until a message is available or max retries reached
                while retry_count < max_retries:
                    retry_count += 1
                    st.write(f"Checking for message response... Attempt {retry_count}/{max_retries}")

                    # Retrieve messages from the thread to check if the assistant responded
                    thread_messages = client.beta.threads.messages.list(thread_id=thread.id)

                    # Log messages for debugging
                    st.write(f"Retrieved Messages (Attempt {retry_count}): {thread_messages.data}")

                    # Iterate over the messages
                    for message in thread_messages.data:  # Access the `data` attribute
                        if message.role == 'assistant':
                            st.write(f"Message from Assistant: {message.content}")
                            message_found = True
                            break

                    if message_found:
                        break
                    time.sleep(10)  # Increased sleep duration to 10 seconds between attempts

                if not message_found:
                    st.write("No response from the assistant yet. Please try again later.")

        except Exception as e:
            st.error(f"Error during file upload or analysis: {e}")
            st.write(str(e))  # Log the full exception for better debugging

# =============================
# Everyday Chat Assistant
# =============================

def everyday_chat_assistant():
    st.title("Everyday Chat Assistant")
    user_input = st.text_input("Enter your message:")

    if user_input:
        try:
            # Create or retrieve chat assistant ID from session state
            if not st.session_state.chat_assistant_id:
                st.session_state.chat_assistant_id = create_assistant(
                    instructions="You are a helpful everyday assistant.",
                    model="gpt-4"
                )
                if st.session_state.chat_assistant_id:
                    st.success("Chat Assistant created successfully!")

            # Run the assistant
            if st.session_state.chat_assistant_id:
                response = run_assistant(
                    assistant_id=st.session_state.chat_assistant_id,
                    instructions=user_input
                )
                if response:
                    st.write(response)
            else:
                st.error("Assistant is not initialized.")

        except Exception as e:
            logger.error(f"Error during chat: {e}")
            st.error(f"Error during chat: {e}")

# =============================
# Image Generation Assistant
# =============================

def image_generation_assistant():
    st.title("Image Generation Assistant")
    image_description = st.text_input("Describe the image you want to generate:")

    if image_description:
        try:
            response = openai.Image.create(
                prompt=image_description,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            st.image(image_url)
            logger.info(f"Image generated for prompt: {image_description}")

        except Exception as e:
            logger.error(f"Error during image generation: {e}")
            st.error(f"Error during image generation: {e}")

# =============================
# Main Execution with Navigation using Query Parameters
# =============================

def main():
    # Initialize session state variables
    initialize_session_state()

    # Create three columns for the options like in the image
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Data Analysis Assistant"):
            st.session_state.query_params["page"] = "data_analysis"

    with col2:
        if st.button("Everyday Chat Assistant"):
            st.session_state.query_params["page"] = "everyday_chat"

    with col3:
        if st.button("Image Generation Assistant"):
            st.session_state.query_params["page"] = "image_generation"

    # Determine which page to show based on the query parameter
    page = st.session_state.query_params.get("page", "home")

    if page == "data_analysis":
        data_analysis_assistant()
    elif page == "everyday_chat":
        everyday_chat_assistant()
    elif page == "image_generation":
        image_generation_assistant()
    else:
        st.write("Welcome! Please select an assistant.")

if __name__ == "__main__":
    main()
