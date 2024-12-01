import streamlit as st
from dataAnalyst import data_analysis_assistant
from everydayChat import everyday_chat_assistant
from imageGeneration import image_generation_assistant

# Function to initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'query_params' not in st.session_state:
        st.session_state.query_params = {}

# Custom button with large emoji
def create_large_emoji_button(label, emoji, key):
    button_html = f"""
    <style>
    .large-button {{
        background-color: #4CAF50;
        border: none;
        color: black;
        padding: 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 40px;
        margin: 20px 10px;
        cursor: pointer;
        border-radius: 12px;
        width: 100%;
        height: 170px;
    }}
    .large-button span {{
        font-size: 100px; /* Emoji size increased to 100px */
        display: block;
    }}
    </style>
    <button class="large-button" onclick="window.location.href='{key}'">
        <span>{emoji}</span>
        {label}
    </button>
    """
    st.markdown(button_html, unsafe_allow_html=True)

# Main function to control the app
def main():
    initialize_session_state()

    st.markdown("<h1 style='text-align: center;'>NexGen AI Hub! Please select an Assistant.</h1>", unsafe_allow_html=True)

    # Adjust columns with more space between the main buttons
    col1, empty_col1, col2, empty_col2, col3 = st.columns([1, 0.5, 1, 0.5, 1], gap="large")

    # Displaying the buttons with large emojis
    with col1:
        create_large_emoji_button("Data Analysis Assistant", "📊", "data_analysis")

    with col2:
        create_large_emoji_button("Everyday Chat Assistant", "🤖", "everyday_chat")

    with col3:
        create_large_emoji_button("Image Generation Assistant", "🎨", "image_generation")

    # Handle page changes based on the selected assistant
    page = st.session_state.query_params.get("page", "home")

    if page == "data_analysis":
        data_analysis_assistant()
    elif page == "everyday_chat":
        everyday_chat_assistant()
    elif page == "image_generation":
        image_generation_assistant()
    else:
        st.write("<p style='text-align: center;'>Welcome! Please select an assistant.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
