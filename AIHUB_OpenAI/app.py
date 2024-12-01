import streamlit as st
from dataAnalyst import data_analysis_assistant
from everydayChat import everyday_chat_assistant
from imageGeneration import image_generation_assistant
from flowGeneration import flow_generation_assistant
from sqlAssistant import sql_ai_assistant  # Import the new SQL AI Assistant

def initialize_session_state():
    """Initialize session state variables."""
    if 'query_params' not in st.session_state:
        st.session_state.query_params = {}

def main():
    initialize_session_state()

    st.markdown("<h1 style='text-align: center;'>NexGen AI Hub! Please select an Assistant.</h1>", unsafe_allow_html=True)

    button_style = """
    <style>
    div[data-testid="stHorizontalBlock"] div button {
        font-weight: bold;
        font-size: 100px;
        height: 150px;
        width: 100%;
        border-radius: 10px;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(1) button { background-color: #4CAF50; }
    div[data-testid="stHorizontalBlock"] div:nth-child(2) button { background-color: #FFB6C1; }
    div[data-testid="stHorizontalBlock"] div:nth-child(3) button { background-color: #33C1FF; }
    div[data-testid="stHorizontalBlock"] div:nth-child(4) button { background-color: #FFA500; }
    div[data-testid="stHorizontalBlock"] div:nth-child(5) button { background-color: #D2691E; }
    .emoji { font-size: 50px; display: block; }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)  # Add SQL AI Assistant column

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
        if st.button("📝 Flow Diagram Assistant"):
            st.session_state.query_params["page"] = "flow_generation"

    with col5:
        if st.button("🗄️ SQL AI Assistant"):
            st.session_state.query_params["page"] = "sql_ai"

    # Handle page navigation
    page = st.session_state.query_params.get("page", "home")

    if page == "data_analysis":
        data_analysis_assistant()
    elif page == "everyday_chat":
        everyday_chat_assistant()
    elif page == "image_generation":
        image_generation_assistant()
    elif page == "flow_generation":
        flow_generation_assistant()
    elif page == "sql_ai":
        sql_ai_assistant()
    else:
        st.write("<p style='text-align: center;'>Welcome! Please select an assistant.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
