import streamlit as st
import openai
from modules.file_upload import handle_file_upload, sanitize_json_string
from modules.xml_processing import parse_cxml, flatten_dict
from modules.vector_store import create_vector_store_and_store_cxml_data
from modules.assistant_handler import handle_assistant_response_with_thread



# Accessing the OpenAI API key from secrets
openai.api_key = st.secrets["general"]["OPENAI_API_KEY"]


st.set_page_config(
    page_title="Chat with cXML using AI 💁",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Chat with cXML using AI 💁")

#openai.api_key = st.secrets["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"]
client = openai

uploaded_files = handle_file_upload()
parsed_data = []

if uploaded_files:
    st.write("Parsing uploaded cXML files...")
    for file in uploaded_files:
        data = parse_cxml(file, sanitize_json_string)
        if data:
            parsed_data.append(data)

    for idx, data in enumerate(parsed_data):
        st.subheader(f"Parsed Data from File {idx + 1}")
        flattened_data = flatten_dict(data)
        st.dataframe(flattened_data.items())

vector_store_id = None

user_question = st.text_input("Ask a question about the cXML files:")

if st.button("Ask Assistant"):
    if user_question:
        st.write(f"You entered: {user_question}")
        if vector_store_id is None:
            vector_store_id = create_vector_store_and_store_cxml_data(parsed_data, client)
        handle_assistant_response_with_thread(client, vector_store_id, user_question)
    else:
        st.error("Please enter a question.")
