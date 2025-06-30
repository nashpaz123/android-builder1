# 📦 Android Builder via GCS Triggered Cloud Function

This project enables an end-to-end automation pipeline that builds Android projects triggered by uploading apk Pfile to a Google Cloud Storage (GCS) bucket.

The output is available in the github action pipe: https://github.com/nashpaz123/android-builder1/actions/workflows/build-android.yml 
and links are also available at https://webhook.site/#!/view/78af9619-ca86-42f2-8872-001629e2ab9a/2d407350-2832-4eeb-9b00-7fef3cc82a15/1
To install you may download the file published at release_apk_url (e.g https://storage.googleapis.com/android-builder1-deploy/yetCalc-2025-06-30-18-53/signed-app.apk )

## 🚀 Overview

- Upload a `.zip` file containing an Android project to a GCS bucket.
- A Google Cloud Function is triggered automatically via Eventarc.
- The Cloud Function sends a GitHub API request to dispatch a GitHub Actions workflow.
- The workflow downloads the ZIP, builds the Android project using Gradle, and uploads the APK(s) as GitHub artifacts.
- (Optional) A webhook endpoint can be notified with the build result.

---

## ☁️ GCP Components

- **Cloud Function**: Triggered on `finalized` GCS object events for a specific bucket.
- **Eventarc**: Routes GCS events to the Cloud Function.
- **Pub/Sub**: Used under the hood by Eventarc.
- **Artifact Registry**: Stores Cloud Function container images (auto-managed).
- **IAM**: Ensures Cloud Storage and Eventarc accounts can publish to Pub/Sub.

---

## 🛠️ GitHub Actions Workflow

- Triggered by `workflow_dispatch` via API call.
- Downloads the `.zip` file from GCS.
- Unzips it and builds the Android project using `./gradlew`.
- Uploads resulting `.apk` files.
- Optionally notifies a webhook of success/failure.

---

## 🔐 Environment Variables

The Cloud Function requires these variables to be set:

- `GITHUB_PAT`: A **Fine-Grained or Classic GitHub Token** with `workflows:write` permission.
- `GH_REPO`: Format `username/repository`, e.g. `nashpaz123/android-builder1`.
- `WEBHOOK_URL`: Optional URL to POST build results to.

Set these via the GCP Console, `gcloud functions deploy --set-env-vars`, or an `.env.yaml` file (not committed to Git).

---

## 📦 Deployment

Enable required services:

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  eventarc.googleapis.com \
  eventarcdata.googleapis.com \
  pubsub.googleapis.com
```
Set IAM roles for GCS and Eventarc service accounts:

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

Deploy the function:

```bash
gcloud functions deploy gcs_trigger \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=./gcs_trigger \
  --entry-point=gcs_trigger \
  --env-vars-file=./gcs_trigger/.env.yaml \
  --trigger-event-filters=type=google.cloud.storage.object.v1.finalized \
  --trigger-event-filters=bucket=android-builder1-inputs

```
📁 Upload a Build
Upload your zipped Android project:

```bash
#the project is meant to builds the code from:
wget https://github.com/SimpleMobileTools/Simple-Calculator/archive/refs/heads/master.zip -O simple-calculator.zip
#but basically runs ./gradlew build so can be used with any gradle project 
gsutil cp simple-calculator.zip gs://android-builder1-inputs/simple-calculator-$(date +%s).zip
```
This will trigger the Cloud Function and dispatch the GitHub workflow. see https://webhook.site/78af9619-ca86-42f2-8872-001629e2ab9a and the webhook events at https://webhook.site/#!/view/78af9619-ca86-42f2-8872-001629e2ab9a/aa44aa01-4169-4f3a-b847-b2779290d9be/1

🧪 Testing Locally
To test the GitHub Actions workflow manually:

Go to the Actions tab of your repo.

Select the workflow Build Android.

click Run workflow.

Provide zip_url e.g and (optional atthis point) webhook_url 
