import streamlit as st 
from openai import OpenAI
import logging
import requests  # Import requests to handle HTTP requests
import os  # Import the os module to access environment variables
# Initialize OpenAI client and logger
#client = openai
logger = logging.getLogger(__name__)


# Initialize the OpenAI client
client = OpenAI(api_key='sk')  # Change to your API key

# Set your OpenAI API key from environment variables
openai_api_key = "sk"

# Base URL for OpenAI's DALL·E API
dalle_api_url = "https://api.openai.com/v1/images/generations"

def image_generation_assistant():
    st.title("Image Generation Assistant")

    # Input field to enter the image description (this is the prompt)
    image_description = st.text_input("Describe the image you want to generate:")

    # Button to generate the image
    if image_description:
        if st.button("Generate Image"):
            try:
                # Make a POST request to OpenAI's DALL·E API
                response = requests.post(
                    dalle_api_url,
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": image_description,  # User input as the prompt
                        "n": 1,  # Number of images to generate
                        "size": "1024x1024"  # Size of the image
                    }
                )

                # Check if the request was successful
                if response.status_code == 200:
                    image_url = response.json()['data'][0]['url']
                    st.image(image_url)
                    logger.info(f"Image generated for prompt: {image_description}")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")

            except Exception as e:
                logger.error(f"Error during image generation: {e}")
                st.error(f"Error during image generation: {e}")
        else:
            st.error("Please describe the image to generate.")
