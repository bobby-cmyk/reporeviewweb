import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from github_repo_reader import GitHubRepoReader
from gpt_feedback_provider import GPTFeedbackProvider

app = Flask(__name__)

# Load environment variables
load_dotenv()

def extract_owner_and_repo(github_url):
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        raise ValueError("Invalid GitHub URL format. Expected format: https://github.com/owner/repo")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    repo_url = request.form['repo_url']
    try:
        owner, repo = extract_owner_and_repo(repo_url)
        feedback = process_github_repo(owner, repo)
        return jsonify({'success': True, 'feedback': feedback})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})

def process_github_repo(owner, repo):
    token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not token or not openai_api_key:
        raise ValueError("Missing environment variables. Check your .env file.")

    github_reader = GitHubRepoReader(owner, repo, token)
    tree = github_reader.get_file_tree()

    if not tree:
        return "No files found in the repository."

    directory_structure = ""
    java_files_content = ""
    java_files = []

    for item in tree:
        directory_structure += f"- {item['path']} ({item['type']})\n"
        if item['type'] == 'blob' and item['path'].endswith('.java'):
            java_files.append(item['path'])

    for java_file in java_files:
        java_content = github_reader.fetch_file_content(java_file)
        if java_content:
            java_files_content += f"\n--- {java_file} ---\n{java_content}\n"

    if java_files_content:
        gpt_feedback = GPTFeedbackProvider(api_key=openai_api_key)
        feedback = gpt_feedback.get_feedback(directory_structure, java_files_content)
        return feedback
    else:
        return "No Java files found to analyze."

app = app

# comment to deploy