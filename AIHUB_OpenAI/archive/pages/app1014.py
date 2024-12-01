import streamlit as st
from dataAnalyst import data_analysis_assistant
from everydayChat import everyday_chat_assistant
from imageGeneration import image_generation_assistant
from flowGeneration import flow_generation_assistant  # Import the new assistant

# Function to initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'query_params' not in st.session_state:
        st.session_state.query_params = {}

# Main function to control the app
def main():
    initialize_session_state()

    st.markdown("<h1 style='text-align: center;'>NexGen AI Hub! Please select an Assistant.</h1>", unsafe_allow_html=True)

    # Add custom CSS for colorful buttons and emojis with very bold font
    button_style = """
    <style>
    div[data-testid="stHorizontalBlock"] div:nth-child(1) button {
        background-color: #4CAF50;  /* Green #4CAF50 for Data Analysis */
        color: black;  /* Black font */
        font-weight: bold;  /* Bold font */
        font-size: 100px; /* Larger text size */
        height: 150px;
        width: 100%;
        border-radius: 10px;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(2) button {
        background-color: #FFB6C1;  /* Light Pink #FFB6C1 for Everyday Chat */
        color: black;  /* Black font */
        font-weight: bold;  /* Bold font */
        font-size: 100px; /* Larger text size */
        height: 150px;
        width: 100%;
        border-radius: 10px;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(3) button {
        background-color: #33C1FF;  /* Light Blue for Image Generation */
        color: black;  /* Black font */
        font-weight: bold;  /* Bold font */
        font-size: 100px; /* Larger text size */
        height: 150px;
        width: 100%;
        border-radius: 10px;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(4) button {
        background-color: #FFA500;  /* Orange for Flow Diagram Assistant */
        color: black;  /* Black font */
        font-weight: bold;  /* Bold font */
        font-size: 100px; /* Larger text size */
        height: 150px;
        width: 100%;
        border-radius: 10px;
    }
    .emoji {
        font-size: 50px;  /* Larger emoji size */
        display: block;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)  # Added a 4th column for Flow Diagram Assistant

    # Buttons inside the columns
    with col1:
        if st.button("📊 Data Analysis Assistant"):
            st.session_state.query_params["page"] = "data_analysis"

    with col2:
        if st.button("🤖 Everyday Chat Assistant"):
            st.session_state.query_params["page"] = "everyday_chat"

    with col3:
        if st.button("🎨 Image Generation Assistant"):
            st.session_state.query_params["page"] = "image_generation"

    with col4:
        if st.button("📝 Flow Diagram Assistant"):  # New Flow Diagram Assistant button
            st.session_state.query_params["page"] = "flow_generation"

    # Handle page navigation
    page = st.session_state.query_params.get("page", "home")

    if page == "data_analysis":
        data_analysis_assistant()
    elif page == "everyday_chat":
        everyday_chat_assistant()
    elif page == "image_generation":
        image_generation_assistant()
    elif page == "flow_generation":  # Navigate to Flow Diagram Assistant
        flow_generation_assistant()
    else:
        st.write("<p style='text-align: center;'>Welcome! Please select an assistant.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
