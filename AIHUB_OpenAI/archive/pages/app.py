import streamlit as st
from dataAnalyst import data_analysis_assistant
from everydayChat import everyday_chat_assistant
from imageGeneration import image_generation_assistant

# Function to initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'query_params' not in st.session_state:
        st.session_state.query_params = {}

# Main function to control the app
def main():
    initialize_session_state()

    st.markdown("<h1 style='text-align: center;'>Welcome! Please select an assistant.</h1>", unsafe_allow_html=True)

    # Adjust columns with more space between the main buttons
    col1, empty_col1, col2, empty_col2, col3 = st.columns([1, 0.3, 1, 0.3, 1], gap="large")

    # Add custom CSS for larger buttons and more padding
    button_style = """
    <style>
    .stButton button {
        height: 100px;  /* Increased button height */
        width: 100%;    /* Button width set to 100% of the column */
        font-size: 32px; /* Increased font size */
        padding: 20px;   /* Increased padding for more visual space */
        margin-top: 30px; /* Added margin to push buttons down */
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    with col1:
        if st.button("📈 Data Analysis Assistant", key="data_analysis"):
            st.session_state.query_params["page"] = "data_analysis"
        st.markdown("<p style='text-align: center;'>Drop files into Code-Interpreter and I can help you to analyze and visualize the data.</p>", unsafe_allow_html=True)

    with col2:
        if st.button("🤖 Everyday Chat Assistant", key="everyday_chat"):
            st.session_state.query_params["page"] = "everyday_chat"
        st.markdown("<p style='text-align: center;'>Chat with me for help with everyday tasks.</p>", unsafe_allow_html=True)

    with col3:
        if st.button("🎨 Image Generation Assistant", key="image_generation"):
            st.session_state.query_params["page"] = "image_generation"
        st.markdown("<p style='text-align: center;'>Describe the image you would like to create, and I will generate it for you.</p>", unsafe_allow_html=True)

    page = st.session_state.query_params.get("page", "home")

    if page == "data_analysis":
        data_analysis_assistant()
    elif page == "everyday_chat":
        everyday_chat_assistant()
    elif page == "image_generation":
        image_generation_assistant()
    else:
        st.write("Welcome! Please select an assistant.")

if __name__ == "__main__":
    main()
