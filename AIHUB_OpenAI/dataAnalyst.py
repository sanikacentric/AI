import streamlit as st
import pandas as pd
import logging
import io
from openai import OpenAI
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber

# Initialize the OpenAI API client
#client = OpenAI()
#logger = logging.getLogger(__name__)


# Replace 'your-api-key-here' with your actual OpenAI API key
client = OpenAI(api_key='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')  # Replace with your actual key
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

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF file."""
    text = ''
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text.strip()  # Remove any leading/trailing whitespace

# Function to read and process uploaded files based on their extension
def read_file(uploaded_file, file_extension):
    """Read and process uploaded files based on their extension."""
    file_processors = {
        'csv': lambda f: pd.read_csv(f),
        'xlsx': lambda f: pd.read_excel(f),
        'json': lambda f: pd.read_json(f),
        'txt': lambda f: f.read().decode('utf-8'),
        'pdf': extract_text_from_pdf,
        'docx': lambda f: extract_text_from_docx(f),  # Implement this function if needed
    }
    return file_processors.get(file_extension, lambda f: None)(uploaded_file)

# Function to flatten CSV content into readable text
def flatten_csv_for_assistant(file_content):
    """Convert the CSV content to a more readable format for the assistant."""
    try:
        if isinstance(file_content, pd.DataFrame):
            csv_as_list = file_content.to_dict(orient='records')
            max_rows = 10
            csv_as_list_limited = csv_as_list[:max_rows]
            flattened_data = "\n".join([str(row) for row in csv_as_list_limited])
            return flattened_data
        else:
            return "Invalid file content"
    except Exception as e:
        st.error(f"An error occurred while processing the CSV: {e}")
        return None

# Function to handle assistant response using code interpreter
def handle_assistant_response_with_thread(user_input, file_contents):
    """This function handles the assistant response using the code interpreter for analyzing the file content."""
    try:
        # Combine all text content for analysis
        text_content = ""
        if isinstance(file_contents, pd.DataFrame):
            text_content = flatten_csv_for_assistant(file_contents)
        elif isinstance(file_contents, str):
            text_content = file_contents

        content_to_analyze = (
            f"Here is the content from the uploaded files:\n\n{text_content}\n\n"
            f"Based on this data, please perform the following tasks:\n"
            f"1. Provide a detailed summary of the key points from the data, including insights, trends, and any significant observations.\n"
            f"2. Identify trends or insights from the data.\n"
            f"3. Generate various visualizations including:\n"
            f"   - Bar charts\n"
            f"   - Pie charts\n"
            f"   - Heatmaps\n"
            f"   - Scatter plots\n"
            f"4. Provide the code for each visualization and explain what each represents."
        )

        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that analyzes data. Provide a detailed summary of the data, including key insights and trends. Generate various visualizations including bar charts, pie charts, heatmaps, and scatter plots. Provide the code for visualizations and explain what each represents.",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}],
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
                if hasattr(message, 'text'):
                    st.write(f"**Assistant's Text Response:** {message.text}")
                elif hasattr(message, 'code'):
                    code = message.code
                    try:
                        # Execute the code to create visualizations
                        # Execute the code safely with access to plotting libraries
                        exec(code, {"plt": plt, "pd": pd, "sns": sns})
                        # Now display the plots
                        st.pyplot()  # This should now work correctly
                        plt.clf()  # Clear the figure after displaying

                        #exec(code, globals())
                        # Check for any specific plot variables you expect, e.g., 'plt' for Matplotlib
                        #if 'plt' in globals():
                            #st.pyplot(plt)  # Display the plot created by the executed code
                            #plt.clf()  # Clear the figure for future plots
                    except Exception as e:
                        st.error(f"Error executing visualization code: {e}")
                elif hasattr(message, 'image_file'):
                    image_file = message.image_file
                    image_data = client.files.content(image_file.file_id)
                    image_bytes = image_data.read()
                    st.image(image_bytes, caption="Assistant-generated visualization")
                else:
                    st.write(f"Unhandled content type in the response: {message}")
        else:
            st.error("No relevant data found for this query.")

    except Exception as e:
        st.error(f"An error occurred while handling assistant response: {e}")

# Main function for the data analysis assistant
def data_analysis_assistant():
    st.title("📊 Data Analysis Assistant")

    uploaded_files = st.file_uploader("Upload files", type=list(SUPPORTED_FILE_TYPES.keys()), accept_multiple_files=True)

    if uploaded_files:
        st.write("Processing uploaded files...")
        all_file_contents = []

        for file in uploaded_files:
            file_extension = file.name.split('.')[-1]
            if file_extension in SUPPORTED_FILE_TYPES:
                file_content = read_file(file, file_extension)

                if isinstance(file_content, pd.DataFrame):
                    st.subheader(f"Data from file: {file.name}")
                    st.dataframe(file_content)
                    all_file_contents.append(file_content)
                elif isinstance(file_content, str):
                    st.subheader(f"Text from file: {file.name}")
                    st.text(file_content)
                    all_file_contents.append(file_content)
                else:
                    st.warning(f"Unsupported file type: {file_extension}")

            else:
                st.warning(f"Unsupported file type: {file.name}")

    user_question = st.text_input("Ask a question about the uploaded files:")

    if st.button("Ask Assistant"):
        if user_question and all_file_contents:
            st.write(f"You entered: {user_question}")
            try:
                # Combine all contents for analysis
                combined_contents = "\n\n".join(str(content) for content in all_file_contents)
                handle_assistant_response_with_thread(user_question, combined_contents)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please upload files and enter a question before clicking the button.")

# Run the application
if __name__ == "__main__":
    data_analysis_assistant()
