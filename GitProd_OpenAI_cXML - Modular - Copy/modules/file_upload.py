import re
import streamlit as st

def sanitize_json_string(json_string):
    sanitized_string = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_string)
    return sanitized_string

def handle_file_upload():
    uploaded_files = st.file_uploader("Upload cXML files", type="xml", accept_multiple_files=True)
    return uploaded_files
