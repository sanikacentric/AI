import streamlit as st
from github3 import login
from neo4j import GraphDatabase
from datetime import datetime, timedelta

# Set Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"  # Corrected port for Neo4j
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password1234"  # Replace with your Neo4j password

# Set GitHub authentication details
GITHUB_TOKEN = "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"  # Replace with your GitHub token

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def create_neo4j_session():
    return driver.session()

# Initialize GitHub login
gh = login(token=GITHUB_TOKEN)

# Function to fetch commit data from GitHub
def fetch_commits(repo_name, days):
    repo = gh.repository(*repo_name.split('/'))
    since_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    commits = repo.commits(since=since_date)

    commit_data = []
    for commit in commits:
        commit_data.append({
            "sha": commit.sha,
            "author": commit.author.login if commit.author else "Unknown",
            "message": commit.message,
            "date": commit.commit.committer['date']
        })
    
    return commit_data

# Function to save commit data into Neo4j
def save_commits_to_neo4j(session, repo_name, commits):
    for commit in commits:
        session.run("""
            MERGE (d:Developer {name: $author})
            MERGE (t:Task {name: $message})
            MERGE (c:Commit {sha: $sha, date: $date})
            MERGE (d)-[:MADE]->(c)-[:FOR]->(t)
            SET c.date = $date
            """, 
            author=commit['author'], 
            message=commit['message'], 
            sha=commit['sha'], 
            date=commit['date']
        )

# Streamlit UI for GitHub Graph
st.title("GitHub Commit Tracker")

repo_name = st.text_input("Enter GitHub repository (owner/repo):")

time_range = st.selectbox(
    "Select time range for commits:",
    ("Last 30 days", "Last 10 days", "Last 5 days")
)

days_mapping = {
    "Last 30 days": 30,
    "Last 10 days": 10,
    "Last 5 days": 5
}

if repo_name and time_range:
    st.write(f"Fetching commits for repository: {repo_name} in the {time_range.lower()}")

    session = create_neo4j_session()
    commits = fetch_commits(repo_name, days_mapping[time_range])
    
    if commits:
        save_commits_to_neo4j(session, repo_name, commits)
        st.success(f"Successfully saved {len(commits)} commits to Neo4j!")

        st.write("Developers who made check-ins in the selected period:")
        developers = session.run("""
            MATCH (d:Developer)-[:MADE]->(c:Commit)
            WHERE c.date >= $since_date
            RETURN d.name AS developer, COUNT(c) AS checkins
            """, since_date=(datetime.utcnow() - timedelta(days=days_mapping[time_range])).strftime('%Y-%m-%d'))
        
        for record in developers:
            st.write(f"{record['developer']} made {record['checkins']} check-in(s).")
        
        st.write("Tasks committed in the selected period:")
        tasks = session.run("""
            MATCH (c:Commit)-[:FOR]->(t:Task)
            WHERE c.date >= $since_date
            RETURN t.name AS task, COUNT(c) AS checkins
            """, since_date=(datetime.utcnow() - timedelta(days=days_mapping[time_range])).strftime('%Y-%m-%d'))
        
        for record in tasks:
            st.write(f"Task '{record['task']}' was checked in {record['checkins']} time(s).")
    else:
        st.warning(f"No commits found for the last {days_mapping[time_range]} days.")
    
    session.close()
