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


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to interact with OpenAI API to get the flow description
def generate_flow_description(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4
            messages=[
                {"role": "system", "content": "You are an assistant that generates flow diagrams."},
                {"role": "user", "content": prompt}
            ],
            
            max_tokens=200,
            temperature=0.3,
            n=1
        )
        # Extract the generated response
        #flow_description = response.choices[0].text.strip()
        #logger.info(f"Generated Flow Description: {flow_description}")
        #return flow_description
    #except Exception as e:
        #logger.error(f"Error generating flow description: {e}")
        #return None
        #logger.info(f"API Response: {response}")
        #st.write("Response:")
        #st.write(response)

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

# Function to create a flow diagram using Graphviz
def create_flow_diagram(description, output_file='flow_diagram'):
    try:
        # Create a new directed graph using Graphviz
        diagram = graphviz.Digraph('Flow Diagram', format='png', engine='dot')
        
        # Set graph attributes
        diagram.attr(rankdir='LR', size='10,5')  # Left-to-right layout, wider size
        diagram.attr('node', shape='ellipse', style='filled', fillcolor='lightblue', fontname='Helvetica', fontsize='12')
        diagram.attr('edge', color='black', fontcolor='blue', fontsize='10')

        # Split the description into steps based on '>>' delimiter
        steps = description.split('>>')
        nodes = [step.strip() for step in steps if step.strip()]

        # Add nodes and edges between them in the flow
        for i in range(len(nodes) - 1):
            diagram.edge(nodes[i], nodes[i + 1], label=f"Step {i+1}")

        # Render the diagram and save it to a file
        output_file_path = os.path.abspath(output_file)
        diagram.render(output_file_path)
        logger.info(f"Flow diagram saved as: {output_file_path}.png")
        return output_file_path + ".png"  # Return the generated file path for reference

    except Exception as e:
        logger.error(f"Error generating flow diagram: {e}")
        return None

# Streamlit app to handle user input and generate the flow diagram
def flow_generation_assistant():
    st.title("Flow Generation Assistant")

    # Ask the user to describe their flow
    flow_prompt = st.text_area("Describe the flow you want to visualize:")
    
    # Button to generate the flow diagram
    if st.button("Generate Flow Diagram"):
        if flow_prompt:
            # Generate the flow description using OpenAI GPT model
            flow_description = generate_flow_description(flow_prompt)
            st.write(f"Generated Flow Description:\n{flow_description}")

            if flow_description:
                # Generate the flow diagram
                output_image_path = create_flow_diagram(flow_description)

                # Check if the diagram is generated and display it
                if output_image_path and os.path.exists(output_image_path):
                    st.image(output_image_path, caption='Flow Diagram', use_column_width=True)
                else:
                    st.error("Flow diagram could not be generated or displayed.")
        else:
            st.error("Please enter a flow description.")

# Run the Streamlit application
if __name__ == "__main__":
    flow_generation_assistant()
