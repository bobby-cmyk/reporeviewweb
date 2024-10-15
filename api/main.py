import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from api.github_repo_reader import GitHubRepoReader
from api.gpt_feedback_provider import GPTFeedbackProvider  # Import the GPTFeedbackProvider class
from fastapi import FastAPI, Request, Form
from api.github_repo_reader import GitHubRepoReader
from api.gpt_feedback_provider import GPTFeedbackProvider
from dotenv import load_dotenv
import os

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Create the API route to analyze the repository
@app.post("/analyze")
async def analyze_repo(github_url: str = Form(...)):
    """Analyze the provided GitHub URL and return GPT feedback."""
    try:
        owner, repo = extract_owner_and_repo(github_url)
    except ValueError as e:
        return {"error": str(e)}

    # Load GitHub token and OpenAI API key from environment
    token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not token or not openai_api_key:
        return {"error": "API keys missing"}

    # Initialize GitHubRepoReader and GPTFeedbackProvider
    github_reader = GitHubRepoReader(owner, repo, token)
    gpt_feedback = GPTFeedbackProvider(api_key=openai_api_key)

    # Fetch the directory structure and Java file content
    tree = github_reader.get_file_tree()

    if not tree:
        return {"error": "No files found in the repository."}

    directory_structure = ""
    java_files_content = ""
    java_files = []

    # Build directory structure and collect Java file content
    for item in tree:
        directory_structure += f"- {item['path']} ({item['type']})\n"
        if item['type'] == 'blob' and item['path'].endswith('.java'):
            java_files.append(item['path'])

    # Fetch and append the content of each Java file
    for java_file in java_files:
        java_content = github_reader.fetch_file_content(java_file)
        if java_content:
            java_files_content += f"\n--- {java_file} ---\n{java_content}\n"

    if not java_files_content:
        return {"error": "No Java files found to analyze."}

    # Get GPT feedback
    feedback, model, duration = gpt_feedback.get_feedback(directory_structure, java_files_content)

    return {
        "feedback": feedback,
        "model": model,
        "duration": round(duration, 2)
    }

def extract_owner_and_repo(github_url):
    """Extracts the owner and repository name from the GitHub URL"""
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        owner = path_parts[0]
        repo = path_parts[1]
        return owner, repo
    else:
        raise ValueError("Invalid GitHub URL format. Expected format: https://github.com/owner/repo")
