import streamlit as st
from github3 import login
from neo4j import GraphDatabase
from datetime import datetime

# Set Neo4j connection details
NEO4J_URI = "bolt://localhost:8501"
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
def fetch_commits(repo_name):
    repo = gh.repository(*repo_name.split('/'))
    today = datetime.utcnow().strftime('%Y-%m-%d')
    commits = repo.commits(since=today + 'T00:00:00Z')

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
    today = datetime.utcnow().strftime('%Y-%m-%d')
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

if repo_name:
    st.write(f"Fetching commits for repository: {repo_name}")

    session = create_neo4j_session()
    commits = fetch_commits(repo_name)
    
    if commits:
        save_commits_to_neo4j(session, repo_name, commits)
        st.success(f"Successfully saved {len(commits)} commits to Neo4j!")

        st.write("Developers who made check-ins today:")
        developers = session.run("""
            MATCH (d:Developer)-[:MADE]->(c:Commit)
            WHERE c.date CONTAINS $today
            RETURN d.name AS developer, COUNT(c) AS checkins
            """, today=today)
        
        for record in developers:
            st.write(f"{record['developer']} made {record['checkins']} check-in(s).")
        
        st.write("Tasks committed today:")
        tasks = session.run("""
            MATCH (c:Commit)-[:FOR]->(t:Task)
            WHERE c.date CONTAINS $today
            RETURN t.name AS task, COUNT(c) AS checkins
            """, today=today)
        
        for record in tasks:
            st.write(f"Task '{record['task']}' was checked in {record['checkins']} time(s).")
    else:
        st.warning("No commits found for today.")
    
    session.close()
