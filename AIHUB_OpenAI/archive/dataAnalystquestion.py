import streamlit as st
import openai
import logging
import pandas as pd
import io
import os

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI API client with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set as an environment variable

# Supported file types
SUPPORTED_FILE_TYPES = {
    'csv': 'application/csv',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'json': 'application/json',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Add other supported file types here
}

def read_file(uploaded_file, file_extension):
    """Read and process uploaded files based on their extension."""
    file_processors = {
        'csv': lambda f: pd.read_csv(f),
        'xlsx': lambda f: pd.read_excel(f),
        'json': lambda f: pd.read_json(f),
        'txt': lambda f: f.read().decode('utf-8'),
        # Add more file processing functions here
    }

    # Call the appropriate processing function based on the file extension
    return file_processors.get(file_extension, lambda f: None)(uploaded_file)

def get_assistant_response(instructions, file_content, question):
    """
    Sends a prompt to the OpenAI Chat Completion API and retrieves the assistant's response.
    
    :param instructions: The system prompt to define the assistant's behavior.
    :param file_content: The content of the uploaded file.
    :param question: The user's question about the data.
    :return: Assistant's textual response.
    """
    try:
        # Prepare the system message with instructions
        system_message = {"role": "system", "content": instructions}
        
        # Prepare the user message with the question and file content
        user_message = {
            "role": "user",
            "content": f"Here is the data:\n{file_content}\n\nQuestion: {question}"
        }
        
        # Create the chat completion
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_message, user_message],
            temperature=1,
            top_p=1,
        )
        
        # Extract the assistant's reply
        assistant_reply = response.choices[0].message['content'].strip()
        
        return assistant_reply

    except Exception as e:
        st.error(f"Error getting assistant response: {e}")
        logger.error(f"Error getting assistant response: {e}")
        return None

def data_analysis_assistant():
    st.title("📊 Data Analysis Assistant")

    # File upload widget, supporting various file formats
    uploaded_file = st.file_uploader("📂 Upload your data file", type=list(SUPPORTED_FILE_TYPES.keys()))

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()

        file_content = read_file(uploaded_file, file_extension)
        
        st.subheader("📄 Uploaded File:")
        # Display file content or DataFrame directly
        if isinstance(file_content, pd.DataFrame):
            st.dataframe(file_content)
        else:
            st.text_area("File Content", file_content, height=200)

        # User input to ask questions about the data
        st.subheader("❓ Ask a Question About Your Data:")
        question = st.text_input("Enter your question here:")

        if st.button("🔍 Analyze and Get Results"):
            if question:
                # Define the instructions for the assistant
                instructions = (
                    "You are an expert Data Scientist proficient in Python programming. "
                    "You specialize in analyzing datasets and producing visualizations. "
                    "Your main goal is to help business users explore their data and gain insights. "
                    "You will perform the following steps:\n"
                    "1. Greet the user.\n"
                    "2. If the user has specific questions about the data, use Python to answer them.\n"
                    "3. Perform Exploratory Data Analysis (EDA) on the dataset and explain it in simple terms.\n"
                    "4. Create visualizations that are easy for business users to understand and explain each plot.\n"
                    "5. After analysis, remind the user to verify the outputs."
                )
                
                with st.spinner("Analyzing your data..."):
                    # Get the assistant's response
                    assistant_reply = get_assistant_response(instructions, file_content, question)
                
                if assistant_reply:
                    st.subheader("🤖 Assistant's Response:")
                    st.write(assistant_reply)
            else:
                st.warning("⚠️ Please enter a question about the data.")

if __name__ == "__main__":
    data_analysis_assistant()
