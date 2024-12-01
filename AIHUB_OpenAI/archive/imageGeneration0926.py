import streamlit as st
import openai
import logging

# Initialize OpenAI client and logger
client = openai
logger = logging.getLogger(__name__)

# Set your OpenAI API key here
openai.api_key = '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'

def image_generation_assistant():
    st.title("Image Generation Assistant")

    # Input field to enter the image description (this is the prompt)
    image_description = st.text_input("Describe the image you want to generate:")

    # Button to generate the image
    if image_description:
        if st.button("Generate Image"):
            try:
                # Use DALL·E 2 explicitly for image generation
                response = client.Image.create(
                    prompt=image_description,  # User input as the prompt
                    n=1,  # Number of images to generate
                    size="1024x1024",  # Size of the image
                    model="dall-e-2"  # Explicitly mentioning DALL·E 2 as the model
                )
                
                # Extract the image URL from the response
                image_url = response['data'][0]['url']
                
                # Display the generated image
                st.image(image_url)
                
                # Log the successful generation
                logger.info(f"Image generated using DALL·E 2 for prompt: {image_description}")
            except Exception as e:
                logger.error(f"Error during image generation: {e}")
                st.error(f"Error during image generation: {e}")
        else:
            st.error("Please describe the image to generate.")
