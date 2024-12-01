import pandas as pd
import streamlit as st

def highlight_performance(val):
    """Highlight the best performer in green."""
    color = 'green' if val == 'Top Performer' else ''
    return f'background-color: {color}'

def highlight_pr_performance(val):
    """Highlight the top PR performer in green."""
    color = 'green' if val == 'Top PR Performer' else ''
    return f'background-color: {color}'

def display_performance_data(developer_df, developer_data, total_repos):
    # Display highest and lowest commits section
    st.markdown("### Highest and Lowest Commits")
    
    max_commits = developer_df['commits'].max()
    min_commits = developer_df['commits'].min()

    highest_commit_devs = developer_df[developer_df['commits'] == max_commits][['Developer', 'commits']]
    lowest_commit_devs = developer_df[developer_df['commits'] == min_commits][['Developer', 'commits']]

    highest_commit_devs['Performer'] = 'Top Performer'
    lowest_commit_devs['Performer'] = 'Lowest Performer'

    commit_performance_df = pd.concat([highest_commit_devs, lowest_commit_devs])

    # Apply conditional formatting to the DataFrame
    styled_commit_df = commit_performance_df.style.applymap(highlight_performance, subset=['Performer'])

    # Display the DataFrame
    st.subheader("Top & Lowest Commit Performers")
    st.dataframe(styled_commit_df)

    # Developer PR performance section
    st.markdown("### Developers with Highest and Lowest Total PRs")
    
    # Calculate total PRs (prs_created + prs_merged + prs_closed)
    developer_df['total_prs'] = developer_df['prs_created'] + developer_df['prs_merged'] + developer_df['prs_closed']
    
    max_prs = developer_df['total_prs'].max()
    min_prs = developer_df['total_prs'].min()

    highest_pr_devs = developer_df[developer_df['total_prs'] == max_prs][['Developer', 'total_prs']]
    lowest_pr_devs = developer_df[developer_df['total_prs'] == min_prs][['Developer', 'total_prs']]

    highest_pr_devs['Performer'] = 'Top PR Performer'
    lowest_pr_devs['Performer'] = 'Lowest PR Performer'

    pr_performance_df = pd.concat([highest_pr_devs, lowest_pr_devs])

    # Apply conditional formatting for PR performers
    styled_pr_df = pr_performance_df.style.applymap(highlight_pr_performance, subset=['Performer'])
    
    st.subheader("Top & Lowest PR Performers")
    st.dataframe(styled_pr_df)

    # Display total number of repositories and productivity summary
    st.markdown("### Developer Productivity Overview")
    st.write(f"Total number of repositories: {total_repos}")

    # Display Developer Productivity Report for the last 30 days
    st.subheader("Developer Productivity (Last 30 Days)")
    st.dataframe(developer_df.style.set_table_styles([
        {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}
    ]))

