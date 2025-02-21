import os
import streamlit as st
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit  # Updated import
from langchain_community.utilities import SQLDatabase  # Updated import
from langchain_community.chat_models import ChatOpenAI  # Updated import
from langchain_community.agent_toolkits.sql.base import create_sql_agent  # Updated import

# Set your OpenAI API key (replace with your actual API key or pass it during runtime)
os.environ['OPENAI_API_KEY'] = "sk" 

# PostgreSQL database connection configuration
db_user = "postgres"        # Username from your configuration
db_password = "testsanika"   # Password from your configuration
db_host = "host.docker.internal"  # Use host.docker.internal if running in Docker
db_name = "postgres"         # Database name
db_port = 5432               # Default PostgreSQL port

# Construct the SQLAlchemy connection URI
db_uri = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Initialize the SQL database connection
try:
    db = SQLDatabase.from_uri(db_uri)
except Exception as e:
    st.error(f"Failed to connect to the database: {str(e)}")
    raise

# Initialize the LLM (Language Model) using OpenAI's GPT
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# Create the SQL agent toolkit and executor with the LLM parameter
toolkit = SQLDatabaseToolkit(db=db, llm=llm)  # Pass the LLM to avoid ValidationError
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

def sql_ai_assistant():
    """Streamlit SQL AI Assistant interface."""
    st.title("🗄️ SQL AI Assistant")

    # Input area for SQL queries or database-related questions
    query = st.text_area("Enter your SQL query or ask a database-related question:")
    if st.button("Run Query"):
        if query:
            try:
                with st.spinner("Running your query..."):
                    result = agent_executor.run(query)
                st.success("Query executed successfully!")
                st.write("### Query Result:")
                st.write(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a query or question.")
