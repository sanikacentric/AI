import streamlit as st
import pandas as pd
import logging
import io
from openai import OpenAI
import requests
from PIL import Image

# Initialize the OpenAI API client
client = OpenAI()
logger = logging.getLogger(__name__)

# Supported file types
SUPPORTED_FILE_TYPES = {
    'csv': 'application/csv',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'json': 'application/json',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

# Function to read and process uploaded files based on their extension
def read_file(uploaded_file, file_extension):
    """Read and process uploaded files based on their extension."""
    file_processors = {
        'csv': lambda f: pd.read_csv(f),
        'xlsx': lambda f: pd.read_excel(f),
        'json': lambda f: pd.read_json(f),
        'txt': lambda f: f.read().decode('utf-8'),
    }

    return file_processors.get(file_extension, lambda f: None)(uploaded_file)

# Function to upload file content to OpenAI and return file ID
def upload_file_to_openai(file_content, file_extension):
    """Uploads the file content to OpenAI and returns the file ID."""
    try:
        if isinstance(file_content, pd.DataFrame):
            buffer = io.StringIO()
            file_content.to_csv(buffer, index=False)
            buffer.seek(0)
            file_content = buffer.getvalue()

        file_bytes = io.BytesIO(file_content.encode('utf-8'))
        uploaded_file = client.files.create(file=file_bytes, purpose='assistants')
        st.success(f"File uploaded to OpenAI with ID: {uploaded_file.id}")
        return uploaded_file.id

    except Exception as e:
        st.error(f"File upload failed: {e}")
        logger.error(f"File upload failed: {e}")
        return None

# Function to download the image file from OpenAI
def download_image_file(file_id):
    """Downloads an image file from OpenAI using the file ID."""
    try:
        # Retrieve file information
        file_info = client.files.retrieve(file_id)
        file_url = file_info['data']['url']  # Extract the file URL
        
        # Download the image file using requests
        response = requests.get(file_url)
        if response.status_code == 200:
            image_data = response.content  # Get the binary content of the image
            return Image.open(io.BytesIO(image_data))  # Convert to PIL Image
        else:
            st.error(f"Failed to download image with ID: {file_id}")
            return None
    except Exception as e:
        st.error(f"An error occurred while downloading the image: {e}")
        return None

# Function to handle assistant response using code interpreter
def handle_assistant_response_with_thread(user_input, file_contents):
    """This function handles the assistant response using the code interpreter for analyzing the file content."""
    try:
        # Pass the file content explicitly to the assistant
        content_to_analyze = f"Here is the content of the file:\n\n{file_contents}\n\nNow, {user_input}"

        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that analyzes data, summarizes it, and provides visualizations.",
            model="gpt-4-turbo",
            tools=[{"type": "code_interpreter"}],  # Only using code interpreter now
        )
        st.write("Assistant created successfully with code interpreter capabilities!")

        thread = client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": content_to_analyze,
            }],
        )

        # Poll the run to completion and retrieve the messages
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        if messages:
            for message in messages[0].content:
                if hasattr(message, 'text'):  # If there's text in the response
                    st.write(f"**Assistant's Text Response:** {message.text}")
                elif hasattr(message, 'image'):  # If there's an image (e.g., chart or visualization)
                    # Download the image file from OpenAI and display it
                    image = download_image_file(message.image.image_file.file_id)
                    if image:
                        st.image(image, caption="Assistant-generated chart/visualization")
                else:
                    st.write(f"Unhandled content type in the response: {message}")
        else:
            st.error("No relevant data found for this query.")
    
    except Exception as e:
        st.error(f"An error occurred while handling the assistant response: {e}")

# Main function for the data analysis assistant
def data_analysis_assistant():
    st.title("📊 Data Analysis Assistant")

    # Main section for file upload and parsing
    uploaded_files = st.file_uploader("Upload files", type=list(SUPPORTED_FILE_TYPES.keys()), accept_multiple_files=True)

    if uploaded_files:
        st.write("Processing uploaded files...")

        # Variable to hold all file contents for analysis
        all_file_contents = ""

        # Process and display each uploaded file
        for file in uploaded_files:
            file_extension = file.name.split('.')[-1]
            if file_extension in SUPPORTED_FILE_TYPES:
                file_content = read_file(file, file_extension)

                # Display file content based on type
                if isinstance(file_content, pd.DataFrame):
                    st.subheader(f"Data from file: {file.name}")
                    st.dataframe(file_content)
                    # Add the content as a CSV string for the assistant
                    all_file_contents += file_content.to_csv(index=False)
                elif isinstance(file_content, str):
                    st.subheader(f"Text from file: {file.name}")
                    st.text(file_content)
                    # Append the text content for the assistant
                    all_file_contents += file_content
                else:
                    st.warning(f"Unsupported file type: {file_extension}")

            else:
                st.warning(f"Unsupported file type: {file.name}")

    # User input for assistant interaction
    user_question = st.text_input("Ask a question about the uploaded files:")

    if st.button("Ask Assistant"):
        if user_question and uploaded_files:
            st.write(f"You entered: {user_question}")
            try:
                # Handle assistant response with file contents
                handle_assistant_response_with_thread(user_question, all_file_contents)

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please upload files and enter a question before clicking the button.")
