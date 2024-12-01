import streamlit as st
import logging
from openai import OpenAI
import graphviz
import os  # Import os for path handling

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key='your-api-key-here')  # Change to your API key

def generate_flow_description(prompt): 
    try:
        response = client.chat.completions.create(
            model="gpt-4-o",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are an assistant that generates flow diagrams."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        logger.info(f"API Response: {response}")  # Log the entire response
        st.write("Response:")
        st.write(response)  # Display the full response for debugging
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            if content:  # Check if content is not empty
                return content
            else:
                logger.error("Received empty content from API.")
                return "Error: Received empty content from API."
        else:
            logger.error("No valid response from API.")
            return "No valid response from API."
    except Exception as e:
        logger.error(f"Error in generating flow description: {e}")
        return f"Error generating description: {str(e)}"  # Return the error message

def create_flow_diagram(description, output_file='flow_diagram'):
    # Create a Graphviz diagram with specified size
    diagram = graphviz.Digraph('Flow Diagram', format='png')
    
    # Set attributes for better visibility
    diagram.attr(size='10,10')  # Specify size (width, height) in inches
    diagram.attr('node', shape='rectangle', style='filled', fillcolor='lightgrey', fontsize='12')
    
    # Split description by new lines to extract steps
    steps = description.split('\n')
    
    # Filter out empty lines and process steps
    for step in steps:
        step = step.strip()
        if step and not step.startswith('Below is a textual representation'):
            diagram.node(step)  # Create a node for each step
            
            # This is a simple case; for complex flows, you might need logic to define edges

    # Connect nodes assuming a simple linear flow
    for i in range(len(steps) - 1):
        if steps[i] and steps[i + 1]:
            diagram.edge(steps[i], steps[i + 1])

    diagram.render(os.path.abspath(output_file))  # Use absolute path
    logger.info(f"Flow diagram created as '{output_file}.png'")

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
                create_flow_diagram(flow_description)
                if os.path.exists('flow_diagram.png'):
                    st.image(os.path.abspath('flow_diagram.png'), caption='Flow Diagram')  # Use absolute path
                else:
                    st.error("Flow diagram was not created.")
            else:
                st.error("Failed to generate a valid flow diagram description.")
        else:
            st.error("Please enter a flow description.")

# Run the Streamlit application
if __name__ == "__main__":
    flow_generation_assistant()
