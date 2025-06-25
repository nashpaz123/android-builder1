import functions_framework
import requests
import os

@functions_framework.cloud_event
def gcs_trigger(cloud_event):
    data = cloud_event.data
    name = data["name"]
    bucket = data["bucket"]

    if not name.endswith(".zip"):
        return "Not a zip file."

    zip_url = f"https://storage.googleapis.com/{bucket}/{name}"
    webhook_url = os.environ["WEBHOOK_URL"]

    github_api = "https://api.github.com/repos/nashpaz123/android-builder1/actions/workflows/build-android.yml/dispatches"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_PAT']}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "zip_url": zip_url,
            "webhook_url": webhook_url
        }
    }

    r = requests.post(github_api, json=payload, headers=headers)
    return f"GitHub workflow dispatch status: {r.status_code}"
