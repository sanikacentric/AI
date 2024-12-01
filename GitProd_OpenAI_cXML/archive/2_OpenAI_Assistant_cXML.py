import os
import streamlit as st
import xml.etree.ElementTree as ET
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import openai
import json
import xml.etree.ElementTree as ET
import streamlit as st
import re



#######################
# Page configuration
st.set_page_config(
    page_title="cXML Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded")


# Initialize OpenAI components using LangChain
openai_api_key = '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'
openai.api_key = openai_api_key
client = openai

# Initialize OpenAI components using LangChain
#llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
#embedding_model = OpenAIEmbeddings(openai_api_key='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')


# Custom CSS to center the title
st.markdown("""
<style>
.reportview-container .main .block-container{
    padding-top: 2rem;
}
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Streamlit App Title
st.title("cXML File Assistant")

# Columns Setup
col = st.columns((2, 4, 2), gap='medium')

# Upload multiple cXML files
uploaded_files = st.file_uploader("Upload cXML files", type="xml", accept_multiple_files=True)

# Function to parse and extract cXML data
# Function to parse and extract cXML data
# Function to parse and extract cXML data from the payload


# Function to sanitize and clean JSON content
def sanitize_json_string(json_string):
    sanitized_string = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_string)
    return sanitized_string

# Function to parse and extract cXML data
def parse_cxml(file):
    try:
        # Read the file content
        file_content = file.read().decode('utf-8')

        # Sanitize the JSON string to remove invalid control characters
        sanitized_content = sanitize_json_string(file_content)

        # Parse the sanitized JSON content
        json_data = json.loads(sanitized_content)

        # Extract the 'cxml' field which contains the actual XML data
        cxml_string = json_data.get("payload", {}).get("cxml", None)
        if not cxml_string:
            st.error("No 'cxml' field found in the JSON payload.")
            return None

        # Parse the cXML string
        root = ET.fromstring(cxml_string)

        # Example parsing logic, modify based on your cXML structure
        document_data = {}
        for elem in root.iter():
            document_data[elem.tag] = elem.text

        return document_data

    except ET.ParseError as e:
        st.error(f"Error parsing cXML: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None

# Global variable to store vector store ID
vector_store_id = None

# Placeholder for storing parsed data
parsed_data = []

# If files are uploaded, parse each cXML file
if uploaded_files:
    st.write("Parsing uploaded cXML files...")
    for file in uploaded_files:
        data = parse_cxml(file)
        parsed_data.append(data)

    st.write(f"Parsed data from {len(uploaded_files)} files.")

    # Optionally display parsed data for each file
    for idx, data in enumerate(parsed_data):
        st.subheader(f"Parsed Data from File {idx+1}")
        st.json(data)

# Function to create vector store and store cXML data
def create_vector_store_and_store_cxml_data(parsed_data):
    global vector_store_id  # Reference the global variable to store the ID
    try:
        # Convert the parsed data to a list of dicts
        cxml_data_list = parsed_data

        # Save JSON data to a file
        with open("/tmp/cxml_data.json", "w") as f:
            json.dump(cxml_data_list, f)

        # Upload the file to OpenAI
        upload_response = client.files.create(
            purpose='assistants',
            file=open("/tmp/cxml_data.json", "rb")
        )

        # Access the file ID properly
        file_id = upload_response.id  # Retrieve the file ID from the response object

        st.write(f"File uploaded with ID: {file_id}")

        # Directly return the file ID
        return file_id

    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None

# Function to handle assistant response
def handle_assistant_response_with_thread(file_id, user_input):
    try:
        # Create the assistant first (you can adjust the model as needed)
        assistant = client.beta.assistants.create(
            instructions="You are a helpful assistant that answers questions based on the cXML data.",
            model="gpt-4"
        )
        st.write("Assistant created successfully!")

        # Create a thread for handling the user's query, attaching the file
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please provide insights based on this query: {user_input}",
                    "attachments": [
                        {
                            "file_id": file_id,
                            "tools": [{"type": "file_search"}]
                        }
                    ]
                }
            ]
        )

        # Poll the run to completion and retrieve the messages
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Display the assistant's response
        if messages:
            message_content = messages[0].content[0].text
            st.write(f"**Assistant's Answer:** {message_content}")
        else:
            st.error("No relevant data found for this query in the vector store.")

    except Exception as e:
        st.error(f"An error occurred while handling the assistant response: {e}")

# User input
user_question = st.text_input("Ask a question about the cXML files:")

# Main logic for handling user interaction
if st.button("Ask Assistant"):
    if user_question:
        st.write(f"You entered: {user_question}")

        try:
            # Ensure file_id is properly set
            file_id = create_vector_store_and_store_cxml_data(parsed_data)
            if file_id:
                st.success("Vector store is initialized.")
                # Handle assistant response using threads
                handle_assistant_response_with_thread(file_id, user_question)
            else:
                st.error("File upload failed, unable to initialize vector store.")

        except Exception as e:
            # Handle any error that occurs during the process
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a question before clicking the button.")
