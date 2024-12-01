import streamlit as st
import openai
import tempfile
import os
from openai import OpenAI
from dotenv import load_dotenv  # Importing load_dotenv
import logging

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

#client = OpenAI(api_key ="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")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    logger.error("OpenAI API key not found in environment variables.")
    st.stop()

openai.api_key = openai_api_key

# Initialize the OpenAI client
# Note: Replace `openai.Client` with the appropriate client initialization if different.
# As of September 2021, OpenAI's Python SDK doesn't have a `Client` class.
# Assuming you have access to `beta` features via `openai` directly.
client = openai  # Update this if your SDK uses a different method

# =============================
# Streamlit Sidebar
# =============================

st.sidebar.title("AI Assistant Framework")
assistant_type = st.sidebar.selectbox(
    "Choose your Assistant",
    ("Data Analysis Assistant", "Everyday Chat Assistant", "Image Generation Assistant")
)

# =============================
# Helper Functions
# =============================

def initialize_session_state():
    """Initialize session state variables."""
    if 'data_analysis_assistant_id' not in st.session_state:
        st.session_state.data_analysis_assistant_id = None
    if 'chat_assistant_id' not in st.session_state:
        st.session_state.chat_assistant_id = None

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
                file = client.beta.files.create(
                    file=open(tmp.name, "rb"),
                    purpose='assistants'
                )
            st.success("File uploaded successfully!")
            logger.info(f"File '{file_name}' uploaded successfully with ID: {file['id']}")

            # Create or retrieve assistant ID from session state
            if not st.session_state.data_analysis_assistant_id:
                st.session_state.data_analysis_assistant_id = create_assistant(
                    instructions="You are a personal data analyst. Analyze the uploaded CSV file and generate insights.",
                    model="gpt-4",
                    tools=[{"type": "code_interpreter"}],
                    tool_resources={
                        "code_interpreter": {
                            "file_ids": [file["id"]]
                        }
                    }
                )
                if st.session_state.data_analysis_assistant_id:
                    st.success("Data Analysis Assistant created successfully!")

            # Provide analysis result
            if st.button("Analyze Data"):
                if st.session_state.data_analysis_assistant_id:
                    analysis = run_assistant(
                        assistant_id=st.session_state.data_analysis_assistant_id,
                        instructions="Provide insights and summary about the data.",
                        tools={"code_interpreter": {"file_ids": [file["id"]]}}
                    )
                    if analysis:
                        st.write(analysis)
                else:
                    st.error("Assistant is not initialized.")

        except Exception as e:
            logger.error(f"Error during file upload or analysis: {e}")
            st.error(f"Error during file upload or analysis: {e}")

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
                    # Add tools if necessary
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
# Main Execution
# =============================

def main():
    # Initialize session state variables
    initialize_session_state()

    # Run the selected assistant
    if assistant_type == "Data Analysis Assistant":
        data_analysis_assistant()
    elif assistant_type == "Everyday Chat Assistant":
        everyday_chat_assistant()
    elif assistant_type == "Image Generation Assistant":
        image_generation_assistant()
    else:
        st.error("Unknown assistant type selected.")

if __name__ == "__main__":
    main()
