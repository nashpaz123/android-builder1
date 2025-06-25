import functions_framework
import requests
import os

@functions_framework.cloud_event
def gcs_trigger(cloud_event):
    data = cloud_event.data
    name = data["name"]
    bucket = data["bucket"]

    if not name.endswith(".zip"):
        return "Not a zip file. Skipping."

    # Construct GCS URL for the uploaded zip
    zip_url = f"https://storage.googleapis.com/{bucket}/{name}"

    # Load environment variables
    github_pat = os.environ["GITHUB_PAT"]
    github_repo = os.environ["GH_REPO"]
    webhook_url = os.environ["WEBHOOK_URL"]

    # GitHub API endpoint to trigger workflow_dispatch
    github_api = f"https://api.github.com/repos/{github_repo}/actions/workflows/build-android.yml/dispatches"

    headers = {
        "Authorization": f"Bearer {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": "main",  # must match your default branch name
        "inputs": {
            "zip_url": zip_url,
            "webhook_url": webhook_url
        }
    }

    # Call GitHub API to dispatch workflow
    response = requests.post(github_api, json=payload, headers=headers)

    # Report result to webhook.site
    result = {
        "dispatched": response.status_code == 204,
        "status_code": response.status_code,
        "response": response.text,
        "zip_url": zip_url
    }

    try:
        requests.post(webhook_url, json=result)
    except Exception as e:
        # Optional: log this error somewhere else if webhook fails
        print(f"Webhook POST failed: {e}")

    return f"GitHub workflow dispatch status: {response.status_code}"

