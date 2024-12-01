import streamlit as st
import logging
from openai import OpenAI
import graphviz
import os

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key='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')  # Change to your API key

def generate_flow_description(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are an assistant that generates flow diagrams."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        logger.info(f"API Response: {response}")
        st.write("Response:")
        st.write(response)

        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            if content:
                return content
            else:
                logger.error("Received empty content from API.")
                return "Error: Received empty content from API."
        else:
            logger.error("No valid response from API.")
            return "No valid response from API."
    except Exception as e:
        logger.error(f"Error in generating flow description: {e}")
        return f"Error generating description: {str(e)}"

def create_flow_diagram(description, output_file='flow_diagram'):
    # Use 'dot' engine for hierarchical layout
    diagram = graphviz.Digraph('Flow Diagram', format='png', engine='dot')

    # Split description by '>>' to extract steps
    steps = description.split('>>')

    # Clean up and format nodes
    nodes = [step.strip() for step in steps if step.strip()]

    # Add edges between nodes
    for i in range(len(nodes) - 1):
        diagram.edge(nodes[i], nodes[i + 1], label=f"Step {i+1}")

    # Render the diagram to an absolute path
    output_file_path = os.path.abspath(output_file)
    diagram.render(output_file_path)

    # Log the generated file path
    logger.info(f"Flow diagram created at: {output_file_path}.png")

    return output_file_path + ".png"  # Return the image file path

def flow_generation_assistant():
    st.title("Flow Generation Assistant")
    
    flow_prompt = st.text_area("Describe the flow you want to visualize:", 
                                "Enter any flow description here...")

    if st.button("Generate Flow Diagram"):
        if flow_prompt:
            flow_description = generate_flow_description(flow_prompt)
            st.write("Generated Flow Description:")
            st.write(flow_description)

            # Only create the diagram if flow_description is valid
            if flow_description and "No valid response" not in flow_description:
                output_image_path = create_flow_diagram(flow_description)
                if os.path.exists(output_image_path):
                    st.image(output_image_path, caption='Flow Diagram', use_column_width=True)
                else:
                    st.error(f"Flow diagram was not created at {output_image_path}.")
            else:
                st.error("Failed to generate a valid flow diagram description.")
        else:
            st.error("Please enter a flow description.")

# Run the Streamlit application
if __name__ == "__main__":
    flow_generation_assistant()
