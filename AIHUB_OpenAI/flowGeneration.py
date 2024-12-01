import streamlit as st
import logging
from openai import OpenAI
import networkx as nx

import os
import matplotlib.pyplot as plt
import numpy as np

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key='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')  # Change to your API key


def generate_flow_description(prompt): 
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": "You are an assistant that generates flow diagrams."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
            n=1
        )
        
        logger.info(f"API Response: {response}")  # Log the entire response
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            return content
        else:
            logger.error("No valid response from API.")
            return "No valid response from API."
    except Exception as e:
        logger.error(f"Error in generating flow description: {e}")
        return f"Error generating description: {str(e)}"

def create_flow_diagram(description):
    steps = description.split('\n')
    steps = [step.strip() for step in steps if step.strip()]  # Filter out empty steps

    if not steps:
        logger.error("No valid steps found for the flow diagram.")
        return None  # Early exit if no valid steps

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges based on the steps
    for i in range(len(steps)):
        G.add_node(steps[i])
        if i > 0:
            G.add_edge(steps[i - 1], steps[i])  # Connect current step to the previous step

    # Draw the graph
    plt.figure(figsize=(12, 8))  # Increase figure size for better visibility

    # Use circular layout or shell layout to spread nodes evenly
    pos = nx.circular_layout(G)  # Use circular layout to avoid overlap
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
    
    # Save the figure to a file
    output_file = 'flow_diagram.png'
    plt.title("Flow Diagram")
    plt.savefig(output_file, format='png')
    plt.close()  # Close the plot to free memory
    logger.info(f"Flow diagram created and saved as: {output_file}")

    return output_file

def flow_generation_assistant():
    st.title("Flow Generation Assistant")

    flow_prompt = st.text_area("Describe the flow you want to visualize:")
    
    if st.button("Generate Flow Diagram"):
        if flow_prompt:
            flow_description = generate_flow_description(flow_prompt)
            st.write("Generated Flow Description:")
            st.write(flow_description)

            if flow_description:
                output_image_path = create_flow_diagram(flow_description)
                if output_image_path and os.path.exists(output_image_path):
                    st.image(output_image_path, caption='Flow Diagram', use_column_width=True)
                else:
                    st.error("Flow diagram could not be generated.")
            else:
                st.error("Failed to generate a valid flow diagram description.")
        else:
            st.error("Please enter a flow description.")

# Run the Streamlit application
if __name__ == "__main__":
    flow_generation_assistant()
