import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
import streamlit as st


def plot_commit_charts(developer_df, developer_data, total_repos):
    developers = list(developer_data.keys())
    commits = [developer_data[dev]['commits'] for dev in developers]
    additions = [developer_data[dev]['additions'] for dev in developers]
    deletions = [developer_data[dev]['deletions'] for dev in developers]
    prs_created = [developer_data[dev]['prs_created'] for dev in developers]
    prs_merged = [developer_data[dev]['prs_merged'] for dev in developers]
    prs_closed = [developer_data[dev]['prs_closed'] for dev in developers]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(developers, commits, color='blue', alpha=0.6, label='Commits')
    ax.bar(developers, additions, color='green', alpha=0.6, label='Additions')
    ax.bar(developers, deletions, color='red', alpha=0.6, label='Deletions')
    ax.bar(developers, prs_created, color='orange', alpha=0.6, label='PRs Created')
    ax.bar(developers, prs_merged, color='purple', alpha=0.6, label='PRs Merged')
    ax.bar(developers, prs_closed, color='brown', alpha=0.6, label='PRs Closed')
    ax.set_xlabel('Developers')
    ax.set_ylabel('Count')
    ax.set_title('Developer Productivity Report')
    ax.legend()
    ax.set_xticklabels(developers, rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)


def plot_heatmap(developer_data):
    """Plot a heatmap of commits over time."""
    commit_data = pd.DataFrame(columns=['Date', 'Developer', 'Commits'])

    for dev, data in developer_data.items():
        for commit_detail in data['commit_details']:
            commit_date = pd.to_datetime(commit_detail['commit_date'])  # Access the date from the dictionary
            commit_data = pd.concat([commit_data, pd.DataFrame({'Date': [commit_date],
                                                                'Developer': [dev], 'Commits': [1]})])

    commit_details_df = commit_data.groupby(['Date', 'Developer']).count().reset_index()

    heatmap = alt.Chart(commit_details_df).mark_rect().encode(
        x=alt.X('Developer:N', title='Developer'),
        y=alt.Y('Date:T', title='Date'),
        color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
        tooltip=['Date', 'Developer', 'Commits']
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(heatmap, use_container_width=True)


def plot_scatter(developer_data):
    """Plot a scatter plot of commits over time."""
    developers = list(developer_data.keys())
    fig, ax = plt.subplots(figsize=(12, 8))

    for dev in developers:
        dates = [pd.to_datetime(commit_detail['commit_date']) for commit_detail in developer_data[dev]['commit_details']]
        ax.scatter(dates, [dev] * len(dates), label=dev, alpha=0.6)

    ax.set_xlabel('Date')
    ax.set_ylabel('Developer')
    ax.set_title('Commits per Developer Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)


def plot_altair_charts(developer_data):
    """Plot a circle plot using Altair to represent commit frequency."""
    commit_data = pd.DataFrame(columns=['Date', 'Developer', 'Commits'])

    for dev, data in developer_data.items():
        for commit_detail in data['commit_details']:
            commit_date = pd.to_datetime(commit_detail['commit_date'])  # Access the commit date from the dictionary
            commit_data = pd.concat([commit_data, pd.DataFrame({'Date': [commit_date],
                                                                'Developer': [dev], 'Commits': [1]})])

    circle_plot = alt.Chart(commit_data).mark_circle(size=60).encode(
        x=alt.X('Developer:N', title='Developer'),
        y=alt.Y('Date:T', title='Date'),
        color=alt.Color('Commits:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Commits")),
        tooltip=['Date', 'Developer', 'Commits']
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(circle_plot, use_container_width=True)


def plot_line_chart(developer_data):
    """Plot a line chart showing cumulative commits over time."""
    commit_data = pd.DataFrame(columns=['Date', 'Developer', 'Commits'])

    for dev, data in developer_data.items():
        for commit_detail in data['commit_details']:
            commit_date = pd.to_datetime(commit_detail['commit_date'])
            commit_data = pd.concat([commit_data, pd.DataFrame({'Date': [commit_date],
                                                                'Developer': [dev], 'Commits': [1]})])

    # Ensure Commits column is numeric
    commit_data['Commits'] = pd.to_numeric(commit_data['Commits'])

    commit_data['Cumulative Commits'] = commit_data.groupby('Developer')['Commits'].cumsum()

    line_chart = alt.Chart(commit_data).mark_line().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Cumulative Commits:Q', title='Cumulative Commits'),
        color=alt.Color('Developer:N', title='Developer'),
        tooltip=['Date', 'Developer', 'Cumulative Commits']
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(line_chart, use_container_width=True)


def plot_bar_chart(developer_data):
    """Plot a bar chart of commits aggregated by month."""
    commit_data = pd.DataFrame(columns=['Date', 'Developer', 'Commits'])

    for dev, data in developer_data.items():
        for commit_detail in data['commit_details']:
            commit_date = pd.to_datetime(commit_detail['commit_date'])
            commit_data = pd.concat([commit_data, pd.DataFrame({'Date': [commit_date],
                                                                'Developer': [dev], 'Commits': [1]})])

    commit_data['Date'] = pd.to_datetime(commit_data['Date'])
    commit_data['Month'] = commit_data['Date'].dt.to_period('M')
    commit_data['Month'] = commit_data['Month'].dt.to_timestamp()

    # Ensure Commits column is numeric
    commit_data['Commits'] = pd.to_numeric(commit_data['Commits'])

    bar_chart = alt.Chart(commit_data).mark_bar().encode(
        x=alt.X('Month:T', title='Month'),
        y=alt.Y('sum(Commits):Q', title='Total Commits'),
        color=alt.Color('Developer:N', title='Developer'),
        column='Developer:N',
        tooltip=['Month:T', 'Developer:N', 'sum(Commits):Q']
    ).properties(
        width=200,
        height=400
    )
    st.altair_chart(bar_chart, use_container_width=False)
