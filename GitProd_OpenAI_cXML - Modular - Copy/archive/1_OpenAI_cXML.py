import os
import streamlit as st
import xml.etree.ElementTree as ET
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import SystemMessage, HumanMessage
import openai
import json

# Initialize OpenAI components using LangChain
openai_api_key = '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'


client = OpenAI(api_key ="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",

)
# Initialize OpenAI components using LangChain
llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
embedding_model = OpenAIEmbeddings(openai_api_key='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')


# Page configuration
st.set_page_config(page_title="cXML Document Assistant", layout="wide")

# Streamlit App Title
st.title("cXML Document Assistant")

# Upload multiple cXML files
uploaded_files = st.file_uploader("Upload cXML files", type="xml", accept_multiple_files=True)

# Function to parse and extract cXML data
def parse_cxml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    
    # Example parsing logic (modify as per your specific cXML structure)
    document_data = {}
    for elem in root.iter():
        document_data[elem.tag] = elem.text

    return document_data

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

# Store parsed data in a vector store (mocked here for simplicity)
vector_store = []  # This will be replaced by an actual vector store logic
for data in parsed_data:
    # Convert data to string format for embeddings
    data_string = json.dumps(data)
    embedding = embedding_model.embed(data_string)
    vector_store.append((data, embedding))

# Function to handle user queries
def handle_user_query(query):
    # Mocked search in vector store (replace with actual vector search logic)
    matched_data = None
    for data, embedding in vector_store:
        if query.lower() in json.dumps(data).lower():
            matched_data = data
            break
    
    if matched_data:
        return f"Found relevant data: {json.dumps(matched_data, indent=2)}"
    else:
        return "No relevant data found."

# Allow user to ask a question
user_question = st.text_input("Ask a question about the cXML files:")

if st.button("Ask Assistant"):
    if user_question:
        answer = handle_user_query(user_question)
        st.write(answer)
    else:
        st.write("Please enter a question.")
