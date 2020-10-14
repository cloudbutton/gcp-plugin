# This pluguin has been merged to the official [Lithops repo](https://github.com/lithops-cloud/lithops)

-------

# Lithops Google Cloud Platform Plugin
Lithops plugin for Google Functions and Google Cloud Storage

- Lithops: [https://github.com/lithops-cloud/lithops](https://github.com/lithops-cloud/lithops)

### GCP Account Setup

 1. [Login](https://console.cloud.google.com) to Google Cloud Console (or signup if you don't have an account).
 2. Create a new project. Name it `lithops` or similar.
 3. Navigate to *IAM & Admin* > *Service Accounts*.
 4. Click on *Create Service Account*. Name the service account `lithops-executor` or similar. Then click on *Create*.
 6. Add the following roles to the service account:
	 - Service Account User
	 - Cloud Functions Admin
	 - Pub/Sub Admin
	 - Storage Admin
 7. Click on *Continue*. Then, click on *Create key*. Select *JSON* and then *Create*. Download the JSON file to a secure location in you computer. Click *Done*.
 8. Navigate to *Storage* on the menu. Create a bucket and name it `lithops-data` or similar. Remember to update the corresponding Cloudbutton's config field with this bucket name.

**Note:**  If you don't have access to create new projects or service accounts, ask your account admin to do it for you.

### Local Configuration

Copy the following lines and add them to the local configuration file located in your home directory called `.lithops_config`

```yaml
gcp:
    project_name : <PROJECT_NAME>
    service_account : <SERVICE_ACCOUNT_EMAIL>
    credentials_path : <FULL_PATH_TO_CREDENTIALS_JSON>
    region : <REGION_NAME>
```

 - `project_name`: Project name introduced in step 2 (e.g. `lithops`)
 - `service_account`: Service account email of the service account created on step 4 (e.g. `cloudbutton-executor@lithops.iam.gserviceaccount.com`)
 - `credentials_path`: **Absolute** path of your JSON key file downloaded in step 7 (e.g. `/home/myuser/lithops-invoker1234567890.json`)
 - `region`: Region of the bucket created at step 8. Functions and pub/sub queue will be created in the same region (e.g. `us-east1`)

### Usage

To use GCP functions, change the following lines of your local configuration file:
```yaml
lithops:
    compute_backend : 'gcp_functions'
    storage_backend: 'gcp_storage'
```
