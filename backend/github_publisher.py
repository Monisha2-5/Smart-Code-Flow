import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
API_URL = "https://api.github.com"

def get_headers():
    if not GITHUB_TOKEN:
        raise ValueError("GitHub token is missing in .env configuration.")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def check_repository_exists(repo_name):
    """Check if the repository already exists for the authenticated user."""
    url = f"{API_URL}/repos/{GITHUB_USERNAME}/{repo_name}"
    response = requests.get(url, headers=get_headers())
    return response.status_code == 200

def create_repository(repo_name, description="SmartCodeFlow reviewed project"):
    """Create a new public/private repository on GitHub."""
    if check_repository_exists(repo_name):
        return {"success": True, "message": "Repository already exists."}
    
    url = f"{API_URL}/user/repos"
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": True
    }
    response = requests.post(url, headers=get_headers(), json=payload)
    
    if response.status_code in [200, 201]:
        return {"success": True, "message": "Repository created successfully."}
    else:
        return {"success": False, "error": response.json().get("message", "Unknown error")}

def push_file_to_github(repo_name, file_path, content, commit_message="chore: update via SmartCodeFlow AI"):
    """Push or update a single file in the GitHub repository using the Contents API."""
    url = f"{API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    headers = get_headers()
    
    # Check if file already exists to get its SHA (required by GitHub API for updates)
    get_response = requests.get(url, headers=headers)
    sha = None
    if get_response.status_code == 200:
        sha = get_response.json().get("sha")
        
    # Encode file content to Base64
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": commit_message,
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha
        
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return {"success": True, "file": file_path}
    else:
        return {"success": False, "file": file_path, "error": response.json().get("message", "Failed to push")}