import os
import streamlit as st
from github import Github
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from openai import OpenAI
from langchain.schema import SystemMessage, HumanMessage
import altair as alt
import openai
import json


#######################
# Page configuration
st.set_page_config(
    page_title="GitHub Developer Productivity AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded")

# GitHub Token Environment Variable
os.environ['GITHUB_TOKEN'] = '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'
token = os.getenv('GITHUB_TOKEN')

if not token:
    raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
g = Github(token)


# Initialize OpenAI components using LangChain
llm = ChatOpenAI(openai_api_key='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', model="gpt-4o-mini")
embedding_model = OpenAIEmbeddings(openai_api_key='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')


client = OpenAI(api_key ="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",

)
# Custom CSS to center the title
st.markdown("""
<style>
.reportview-container .main .block-container{
    padding-top: 2rem;
}
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Streamlit App Title
st.title("GitHub Developer Productivity AI")

# Columns Setup
#col1, col2, col3 = st.columns(3)

#######################
# Dashboard Main Panel
col = st.columns((2, 4, 2), gap='medium')

# Dropdown for Organization Selection
org_name = st.sidebar.text_input("Enter Organization Name:", value="sanikacentric")

repo_name = st.sidebar.text_input("Enter Repository Name:", value="streamlit")


# Date Range
days = st.sidebar.slider("Select the number of days:", min_value=1, max_value=365, value=30)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# Set the timezone to EST (New York)
est = pytz.timezone('America/New_York')

# Make start_date and end_date offset-aware by converting them to EST timezone
start_date = est.localize(start_date)
end_date = est.localize(end_date)

# Fetch Repository Data
repo = g.get_repo(f"{org_name}/{repo_name}")
total_repos = g.get_user().get_repos().totalCount

# Initialize Data Collection
developer_data = {}
developer_texts = []
# Function to create vector store and store GitHub data
# After creating the vector store, print out its details to ensure it contains the correct data
def create_vector_store_and_store_github_data(developer_df):
    global vector_store_id
    try:
        # Convert the dataframe to JSON
        developer_data_str = developer_df.to_json()

        # Save JSON data to a file
        with open("/tmp/developer_data.json", "w") as f:
            f.write(developer_data_str)

        # Upload the file to OpenAI
        upload_response = client.files.create(
            purpose='user_data',
            file=open("/tmp/developer_data.json", "rb")
        )
        file_id = upload_response.id

        # Now create the vector store with the uploaded file
        vector_store = client.beta.vector_stores.create(
            name="GitHub Data Vector Store",
            file_ids=[file_id]
        )
        vector_store_id = vector_store.id
        
        # Print or log the contents of the vector store
        st.write(f"Vector store created successfully with ID: {vector_store_id}")
        st.write(f"Vector store contains: {developer_data_str}")

    except Exception as e:
        st.error(f"Failed to create vector store: {e}")
        return None
    
    return vector_store_id




def query_vector_store(vector_store_id, user_input2):
    """
    This function queries the OpenAI vector store with the given vector_store_id and user input.
    """
    try:
        # Querying the vector store
        response = client.beta.vector_stores.query(
            vector_store_id=vector_store_id,
            queries=[{"query": user_input2}]
        )
        
        # Parse the result and return a formatted response
        if response and response.get('data'):
            result = response['data'][0]['document']  # Assuming the first result is the best match
            return f"Found result from vector store: {result}"
        else:
            return "No relevant data found in the vector store."
    except Exception as e:
        return f"Error querying vector store: {e}"

# Fetch Issues within the date range
issues = repo.get_issues(state='all', since=start_date)

for issue in issues:
    if issue.created_at >= start_date and issue.created_at <= end_date:
        creator = issue.user.login if issue.user else 'Unknown'
        assignees = [assignee.login for assignee in issue.assignees] if issue.assignees else []
        
        if creator not in developer_data:
            developer_data[creator] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'code_reviews': 0,
                'issues_created': 0,  # Initialize issue resolution fields
                'issues_assigned': 0,
                'issues_resolved': 0,
                'affected_files': set()
            }
        
        # Track issues created
        developer_data[creator]['issues_created'] += 1
        
        # Track issues assigned
        for assignee in assignees:
            if assignee not in developer_data:
                developer_data[assignee] = {
                    'commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'total_changes': 0,
                    'commit_frequency': 0,
                    'commit_details': [],
                    'prs_created': 0,
                    'prs_merged': 0,
                    'prs_closed': 0,
                    'prs_reviewed': 0,
                    'code_reviews': 0,
                    'issues_created': 0,
                    'issues_assigned': 0,
                    'issues_resolved': 0,
                    'affected_files': set()
                }
            developer_data[assignee]['issues_assigned'] += 1
        
        # Track issues resolved
        if issue.state == 'closed':
            closer = issue.closed_by.login if issue.closed_by else 'Unknown'
            if closer not in developer_data:
                developer_data[closer] = {
                    'commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'total_changes': 0,
                    'commit_frequency': 0,
                    'commit_details': [],
                    'prs_created': 0,
                    'prs_merged': 0,
                    'prs_closed': 0,
                    'prs_reviewed': 0,
                    'code_reviews': 0,
                    'issues_created': 0,
                    'issues_assigned': 0,
                    'issues_resolved': 0,
                    'affected_files': set()
                }
            developer_data[closer]['issues_resolved'] += 1

# Fetch Pull Requests and filter them manually
pulls = repo.get_pulls(state='closed', sort='created', direction='desc', base='main')

# Filter pull requests within the date range
filtered_pulls = [pull for pull in pulls if pull.created_at >= start_date and pull.created_at <= end_date]

# Initialize PR counters for each developer
for pull in filtered_pulls:
    author = pull.user.login if pull.user else 'Unknown'
    if author not in developer_data:
        developer_data[author] = {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'total_changes': 0,
            'commit_frequency': 0,
            'commit_details': [],
            'prs_created': 0,
            'prs_merged': 0,
            'prs_closed': 0,
            'prs_reviewed': 0,
            'code_reviews': 0,  # Initialize code reviews
            'affected_files': set()
        }
    
    # Count PRs
    developer_data[author]['prs_created'] += 1
    if pull.merged_at:
        developer_data[author]['prs_merged'] += 1
    if pull.state == 'closed':
        developer_data[author]['prs_closed'] += 1

        # Count code reviews
    reviews = pull.get_reviews()
    for review in reviews:
        reviewer = review.user.login if review.user else 'Unknown'
        if reviewer not in developer_data:
            developer_data[reviewer] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'code_reviews': 0,  # Initialize code reviews
                'affected_files': set()
            }
        developer_data[reviewer]['code_reviews'] += 1

        # Adding fields for Commit Merge and PR Open in developer_data
for dev in developer_data:
    developer_data[dev]['commit_merge'] = 0  # Initialize commit_merge field
    developer_data[dev]['prs_open'] = 0       # Initialize pr_open field

# Iterate Over Commits
for commit in repo.get_commits(since=start_date, until=end_date):
    author = commit.author.login if commit.author else 'Unknown'
    additions = commit.stats.additions
    deletions = commit.stats.deletions
    total_changes = additions + deletions
    files = [file.filename for file in commit.files]

    if author not in developer_data:
        developer_data[author] = {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'total_changes': 0,
            'commit_frequency': 0,
            'commit_details': [],
            'prs_created': 0,
            'prs_open': 0,       # Initialize pr_open field
            'prs_merged': 0,
            'prs_closed': 0,
            'prs_reviewed': 0,
            'affected_files': set(),
            'commit_merge': 0,  # Initialize commit_merge field
            
        }

    developer_data[author]['commits'] += 1
    developer_data[author]['additions'] += additions
    developer_data[author]['deletions'] += deletions
    developer_data[author]['total_changes'] += total_changes
    developer_data[author]['commit_frequency'] = developer_data[author]['commits'] / days
    developer_data[author]['affected_files'].update(files)
    
    commit_detail = f"Commit: '{commit.commit.message}', Additions: {additions}, Deletions: {deletions}, Total changes: {total_changes}"
    developer_data[author]['commit_details'].append(commit_detail)

    developer_texts.append(f"{author} made the following commit in {repo_name}: {commit_detail}")

# Count commit merges (simple heuristic by checking for "Merge" in the message)
    if "merge" in commit.commit.message.lower():
        developer_data[author]['commit_merge'] += 1

# Process pull request commits
for pull in filtered_pulls:
    pr_commits = pull.get_commits()
    for pr_commit in pr_commits:
        pr_author = pr_commit.author.login if pr_commit.author else 'Unknown'
        pr_additions = pr_commit.stats.additions
        pr_deletions = pr_commit.stats.deletions
        pr_total_changes = pr_additions + pr_deletions
        pr_files = [file.filename for file in pr_commit.files]

        if pr_author not in developer_data:
            developer_data[pr_author] = {
                'commits': 0,
                'additions': 0,
                'deletions': 0,
                'total_changes': 0,
                'commit_frequency': 0,
                'commit_details': [],
                'prs_created': 0,
                'prs_open': 0 ,      # Initialize pr_open field
                'prs_merged': 0,
                'prs_closed': 0,
                'prs_reviewed': 0,
                'affected_files': set(),
                'commit_merge': 0,  # Initialize commit_merge field
                
            }

        developer_data[pr_author]['commits'] += 1
        developer_data[pr_author]['additions'] += pr_additions
        developer_data[pr_author]['deletions'] += pr_deletions
        developer_data[pr_author]['total_changes'] += pr_total_changes
        developer_data[pr_author]['commit_frequency'] = developer_data[pr_author]['commits'] / days
        developer_data[pr_author]['affected_files'].update(pr_files)

        pr_commit_detail = f"PR Commit: '{pr_commit.commit.message}', Additions: {pr_additions}, Deletions: {pr_deletions}, Total changes: {pr_total_changes}"
        developer_data[pr_author]['commit_details'].append(pr_commit_detail)

        developer_texts.append(f"{pr_author} made the following PR commit in {repo_name}: {pr_commit_detail}")
  # Count open PRs
        developer_data[pr_author]['prs_open'] += 1

# Convert developer data to a pandas DataFrame for tabular display
developer_df = pd.DataFrame.from_dict(developer_data, orient='index')
developer_df.reset_index(inplace=True)
developer_df.rename(columns={'index': 'Developer'}, inplace=True)

# Convert affected files from set to a comma-separated string
developer_df['affected_files'] = developer_df['affected_files'].apply(lambda x: ', '.join(x))


with col[0]:
    #st.markdown('#### Highest/Lowest Commits')

    # Calculate the developer with the highest and lowest commits
    max_commits = developer_df['commits'].max()
    min_commits = developer_df['commits'].min()

    highest_commit_developers = developer_df[developer_df['commits'] == max_commits][['Developer', 'commits']]
    lowest_commit_developers = developer_df[developer_df['commits'] == min_commits][['Developer', 'commits']]

    # Add a new column to indicate whether the commit count is the highest or lowest
    highest_commit_developers['Performer'] = 'Best Performer'
    lowest_commit_developers['Performer'] = 'Average Performer'

    # Combine the highest and lowest commit developers into one table
    commit_extremes_df = pd.concat([highest_commit_developers, lowest_commit_developers])

    # Function to apply conditional formatting
    def highlight_best_performer(val):
        color = 'green' if val == 'Best Performer' else ''
        return f'background-color: {color}'

    # Apply the conditional formatting
    styled_commit_extremes_df = commit_extremes_df.style.applymap(highlight_best_performer, subset=['Performer'])

    # Display the new table on Streamlit
    st.subheader("Developers with Highest and Lowest Commits")
    st.dataframe(styled_commit_extremes_df)

    # Add a new column for total PRs (prs_created + prs_merged + prs_closed)
    developer_df['total_prs'] = developer_df['prs_created'] + developer_df['prs_merged'] + developer_df['prs_closed']

    # Find the developer with the highest and lowest total PRs
    max_prs = developer_df['total_prs'].max()
    min_prs = developer_df['total_prs'].min()

    highest_pr_developers = developer_df[developer_df['total_prs'] == max_prs][['Developer', 'total_prs']]
    lowest_pr_developers = developer_df[developer_df['total_prs'] == min_prs][['Developer', 'total_prs']]

    # Add a new column to indicate whether the total PR count is the highest or lowest
    highest_pr_developers['Performer'] = 'Highest PR Performer'
    lowest_pr_developers['Performer'] = 'Lowest PR Performer'

    # Combine the highest and lowest PR developers into one table
    pr_extremes_df = pd.concat([highest_pr_developers, lowest_pr_developers])

    # Function to apply conditional formatting
    def highlight_pr_performer(val):
        color = 'green' if val == 'Highest PR Performer' else ''
        return f'background-color: {color}'

    # Apply the conditional formatting for highest and lowest PR performers
    styled_pr_extremes_df = pr_extremes_df.style.applymap(highlight_pr_performer, subset=['Performer'])

    # Display the new table on Streamlit
    st.subheader("Developers with Highest and Lowest Total PRs")
    st.dataframe(styled_pr_extremes_df)


    # Display total number of repositories
    st.write(f"Total number of repositories: {total_repos}")


    # Calculate total commit frequency
    total_commit_frequency = sum([data['commit_frequency'] for data in developer_data.values()])

    # Display the DataFrame with the applied styling
    st.subheader("Developer Productivity Report (Last 30 Days)")
    st.dataframe(developer_df.style.set_table_styles([
        {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}
    ]))
# Initialize a global variable to store the vector store ID
vector_store_id = None

with col[1]:
    # Ensure 'code_reviews' exists for all developers
    for dev, data in developer_data.items():
        if 'code_reviews' not in data:
            data['code_reviews'] = 0  # Set to 0 if it doesn't exist

    # Ensure all issue resolution keys exist for every developer
    for dev, data in developer_data.items():
        if 'issues_created' not in data:
            data['issues_created'] = 0
        if 'issues_assigned' not in data:
            data['issues_assigned'] = 0
        if 'issues_resolved' not in data:
            data['issues_resolved'] = 0

    # Ensure assistant creation passes vector_store_id properly
    def create_openai_assistant_with_vector_store(vector_store_id):
        """
        Creates an OpenAI Assistant with the vector store for analyzing GitHub data.
        """
        try:
            if vector_store_id is None:
                raise ValueError("Vector store ID is None. Please check if the vector store was created successfully.")

            # Create the OpenAI Assistant
            assistant = client.beta.assistants.create(
                name="GitHub Data Visualizer",
                description="You analyze developer data from the vector store and create insights. Generate trends and visualizations based on the provided data.",
                model="gpt-4o",
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store_id]  # Ensure this is properly set
                    }
                }
            )
            st.write("Assistant with vector store created successfully!")
        except Exception as e:
            st.error(f"Failed to create assistant: {e}")

            # Main logic for handling user interaction
    st.subheader("Developer Productivity Bot")
    user_input2 = st.text_input("Ask a question about the developer productivity data:")

    if st.button("Ask Assistant"):
        if user_input2:
            st.write(f"You entered: {user_input2}")
            
            try:
                # Ensure vector_store_id is properly set
                if vector_store_id is None:
                    vector_store_id = create_vector_store_and_store_github_data(developer_df)
                    create_openai_assistant_with_vector_store(vector_store_id)
                    st.success("Vector store is initialized.")
                else:
                    st.warning("Vector store is already initialized.")

                # Query the vector store and return the result
                vector_store_response = query_vector_store(vector_store_id, user_input2)

                # Perform OpenAI chat completion using the queried vector store response
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides descriptive answers based on the GitHub data vector store."},
                        {"role": "user", "content": f"User query: {user_input2}"},
                        {"role": "assistant", "content": f"Vector store response: {vector_store_response}"}
                    ]
                )

                # Display the response from the assistant
                st.write("**Assistant's Answer:**")
                st.write(chat_completion.choices[0].message.content)

            except Exception as e:
                # Handle any error that occurs during the process
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a question before clicking the button.")
        



with col[2]:
    # Add a button at the top-right corner to enable/disable all charts
    st.markdown("<style>.stButton button {position: absolute; top: 0px; right: 0px;}</style>", unsafe_allow_html=True)
    show_charts = st.checkbox('Enable/Disable All Charts', value=True)
    if show_charts:
        st.markdown('#### Plot for Commits, Additions, and Deletions')

        # Plot Data for Commits, Additions, and Deletions
        developers = list(developer_data.keys())
        commits = [developer_data[dev]['commits'] for dev in developers]
        additions = [developer_data[dev]['additions'] for dev in developers]
        deletions = [developer_data[dev]['deletions'] for dev in developers]
        prs_created = [developer_data[dev]['prs_created'] for dev in developers]
        prs_merged = [developer_data[dev]['prs_merged'] for dev in developers]
        prs_closed = [developer_data[dev]['prs_closed'] for dev in developers]

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        # Set the background color of the figure and the axes
        fig1.patch.set_facecolor('black')
        ax1.set_facecolor('black')

        # Set the color of the axes labels and title to white for better visibility
        ax1.tick_params(colors='white', which='both')
        ax1.xaxis.label.set_color('white')
        ax1.yaxis.label.set_color('white')
        ax1.title.set_color('white')
        ax1.bar(developers, commits, color='blue', alpha=0.6, label='Commits')
        ax1.bar(developers, additions, color='green', alpha=0.6, label='Additions')
        ax1.bar(developers, deletions, color='red', alpha=0.6, label='Deletions')
        ax1.bar(developers, prs_created, color='orange', alpha=0.6, label='PRs Created')
        ax1.bar(developers, prs_merged, color='purple', alpha=0.6, label='PRs Merged')
        ax1.bar(developers, prs_closed, color='brown', alpha=0.6, label='PRs Closed')
        ax1.set_xlabel('Developers')
        ax1.set_ylabel('Count')
        ax1.set_title('Developer Productivity Report')
        ax1.legend()
        ax1.set_xticklabels(developers, rotation=45, ha="right", color='white')
        # Add legend with white text
        legend = ax1.legend(loc='upper right')
        for text in legend.get_texts():
            text.set_color('white')

        plt.tight_layout()

        # Show the plot for Commits, Additions, Deletions, and PRs
        st.pyplot(fig1)

        ################################## added heat map
        
        st.markdown("<h3 style='text-align: center;'>Heat Map</h3>", unsafe_allow_html=True)

        # Initialize DataFrame to store commit data
        columns = ['Date', 'Developer', 'Commits', 'Repository']
        commit_data = pd.DataFrame(columns=columns)

        # Fetch commits within the date range
        commits = repo.get_commits(since=start_date, until=end_date)
        for commit in commits:
            commit_date = commit.commit.author.date.date()  # Get just the date part
            developer = commit.author.login if commit.author else 'Unknown'
            repo_name = repo.name  # Repository name for the commit
            # Create a new DataFrame for the current commit and concatenate it with the main DataFrame
            new_row = pd.DataFrame({'Date': [commit_date], 'Developer': [developer], 'Commits': [1], 'Repository': [repo_name]})
            commit_data = pd.concat([commit_data, new_row], ignore_index=True)

        # Group by Date, Developer, and Repository to count commits
        commit_details_df = commit_data.groupby(['Date', 'Developer', 'Repository']).count().reset_index()

        # Now creating the Altair heatmap
        heatmap_with_repo = alt.Chart(commit_details_df).mark_rect().encode(
            x=alt.X('Developer:N', title='Developer'),
            y=alt.Y('Date:T', title='Date'),
            color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
            tooltip=['Date', 'Developer', 'Commits', 'Repository']
        ).properties(
            width=800,
            height=400
        )

        st.altair_chart(heatmap_with_repo, use_container_width=True)
                
        ################################## end of  heat map

        #########start of scatter plot ##########

        st.markdown("<h3 style='text-align: center;'>Scatter Plot</h3>", unsafe_allow_html=True)


        # Matplotlib scatter plot
        fig, ax = plt.subplots(figsize=(12, 8))
        # Set the background color of the figure and the axes
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        # Set the color of the axes labels and title to white for better visibility
        ax.tick_params(colors='white', which='both')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        # Plot each developer's commits
        for dev in developers:
            dev_data = commit_details_df[commit_details_df['Developer'] == dev]
            ax.scatter(dev_data['Date'], [dev] * len(dev_data), s=dev_data['Commits']*10, label=dev, alpha=0.6)

        ax.set_xlabel('Date')
        ax.set_ylabel('Developer')
        ax.set_title('Commits per Developer Over Time')
        ax.legend(loc='upper right', facecolor='black', edgecolor='white', labelcolor='white')
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        plt.tight_layout()

        st.pyplot(fig)

        #############End of scatter plot ###############

        ############Atlair chart#############

        st.markdown("<h3 style='text-align: center;'>Altair Chart</h3>", unsafe_allow_html=True)

        # Prepare data for Altair chart
        commit_details_df = pd.DataFrame(commit_details_df)
        commit_details_df['Repository'] = repo_name

        # Altair circle plot
        circle_plot = alt.Chart(commit_details_df).mark_circle(size=60).encode(
            x=alt.X('Developer:N', title='Developer'),
            y=alt.Y('Date:T', title='Date'),
            color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
            tooltip=['Date', 'Developer', 'Commits', 'Repository']
        ).properties(
            width=800,
            height=400
        )
        st.altair_chart(circle_plot, use_container_width=True)

        ############end of atlair chart#########

        ##########start of line chart###########

        
        st.markdown("<h3 style='text-align: center;'>Line Chart</h3>", unsafe_allow_html=True)

        # Prepare cumulative commit data
        commit_details_df['Cumulative Commits'] = commit_details_df.groupby('Developer')['Commits'].cumsum()

        # Altair line chart
        line_chart = alt.Chart(commit_details_df).mark_line().encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Cumulative Commits:Q', title='Cumulative Commits'),
            color=alt.Color('Developer:N', title='Developer'),
            tooltip=['Date', 'Developer', 'Cumulative Commits', 'Repository']
        ).properties(
            width=800,
            height=400
        )
        st.altair_chart(line_chart, use_container_width=True)

    ###########end of line chart#######################################################

    ################start of bar chart##############

        st.markdown("<h3 style='text-align: center;'>Altair Bar Chart</h3>", unsafe_allow_html=True)

        # Ensure the 'Date' column is in datetime format
        commit_details_df['Date'] = pd.to_datetime(commit_details_df['Date'])

        # Aggregate the data by month
        commit_details_df['Month'] = commit_details_df['Date'].dt.to_period('M')

        # Convert the 'Month' back to a datetime object for Altair
        commit_details_df['Month'] = commit_details_df['Month'].dt.to_timestamp()

        # Altair bar chart aggregated by month
        bar_chart = alt.Chart(commit_details_df).mark_bar().encode(
            x=alt.X('Month:T', title='Month'),  # Aggregate by month
            y=alt.Y('sum(Commits):Q', title='Total Commits'),  # Sum commits per month
            color=alt.Color('Developer:N', title='Developer'),
            column='Developer:N',
            tooltip=['Month:T', 'Developer:N', 'sum(Commits):Q', 'Repository:N']
        ).properties(
            width=200,
            height=400
        )
        st.altair_chart(bar_chart, use_container_width=False)
    #####################end of bar chart ###############
