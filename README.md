# ADK Short Bot

A Python-based agent that helps shorten messages using Google's Agent Development Kit (ADK) and Vertex AI. See the [Youtube video](https://www.youtube.com/watch?v=bPtKnDIVEsg) for details.

## Prerequisites

- Python 3.12+
- Poetry (Python package manager)
- Google Cloud account with Vertex AI API enabled
- Google Cloud CLI (`gcloud`) installed and authenticated
  - Follow the [official installation guide](https://cloud.google.com/sdk/docs/install) to install gcloud
  - After installation, run `gcloud init` and `gcloud auth login`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bhancockio/deploy-adk-agent-engine.git
   cd adk-short-bot
   ```

2. Install Poetry if you haven't already:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install project dependencies:

   ```bash
   poetry install
   ```

4. Activate the virtual environment:

   ```bash
   source $(poetry env info --path)/bin/activate
   ```

## Configuration

**Getting your Google Cloud Project ID:**

- Method 1: Use gcloud CLI: `gcloud config get-value project`
- Method 2: Check the Google Cloud Console URL when you're in your project: `https://console.cloud.google.com/home/dashboard?project=YOUR-PROJECT-ID`
- Method 3: In Google Cloud Console, the project ID is shown in the project selector dropdown at the top of the page

1. Create a `.env` file in the project root with the following variables:

   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=your-location  # e.g., us-central1
   GOOGLE_CLOUD_STAGING_BUCKET=gs://your-bucket-name
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account-key.json
   ```

2. Set up Google Cloud authentication using service account:

   a. Create a service account in your Google Cloud project:

   ```bash
   gcloud iam service-accounts create adk-bot-sa --display-name="ADK Bot Service Account"
   ```

   b. Grant necessary permissions to the service account:

   ```bash
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:adk-bot-sa@your-project-id.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:adk-bot-sa@your-project-id.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

   c. Create and download the service account key:

   ```bash
   gcloud iam service-accounts keys create ./credentials/service-account-key.json \
     --iam-account=adk-bot-sa@your-project-id.iam.gserviceaccount.com
   ```

   d. The service account key file should be placed in the `credentials/` directory and referenced by the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

   **Note:** If you already have an existing service account (like `react-agent-sa@react-agent-467614.iam.gserviceaccount.com`), you can skip step 2a and use the existing one.

   **Service Account Management:**
   - To list existing service accounts, use your personal Google account: `gcloud auth login && gcloud iam service-accounts list`
   - Service accounts follow the principle of least privilege - they only have permissions needed for their specific tasks
   - For administrative tasks (like listing service accounts), use your personal Google account rather than the service account

3. Enable required APIs:

   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

## Usage

### Local Testing

```bash
poetry run deploy-local
```

### Web Interface

```bash
adk web
```

### Remote Deployment

**Getting your Resource ID:**

After deploying the agent (step 1 below), the resource ID will be displayed in the output. It typically looks like:
`projects/YOUR-PROJECT-ID/locations/YOUR-LOCATION/reasoningEngines/RESOURCE-ID`

To list all existing deployments and their resource IDs:

```bash
poetry run deploy-remote --list
```

1. Deploy the agent:

   ```bash
   poetry run deploy-remote --create
   ```

2. Create a session:

   ```bash
   poetry run deploy-remote --create_session --resource_id=your-resource-id
   ```

3. List sessions:

   ```bash
   poetry run deploy-remote --list_sessions --resource_id=your-resource-id
   ```

4. Send a message:

   ```bash
   poetry run deploy-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Hello, how are you doing today? So far, I've made breakfast today, walkted dogs, and went to work."
   ```

5. Clean up (delete deployment):

   ```bash
   poetry run deploy-remote --delete --resource_id=your-resource-id
   ```

## Project Structure

```text
adk-short-bot/
├── adk_short_bot/          # Main package directory
│   ├── __init__.py
│   ├── agent.py           # Agent implementation
│   └── prompt.py          # Prompt templates
├── deployment/            # Deployment scripts
│   ├── local.py          # Local testing script
│   └── remote.py         # Remote deployment script
├── .env                  # Environment variables
├── poetry.lock          # Poetry lock file
└── pyproject.toml       # Project configuration
```

## Development

To add new features or modify existing ones:

1. Make your changes in the relevant files
2. Test locally using the local deployment script
3. Deploy to remote using the remote deployment script
4. Update documentation as needed

## Troubleshooting

1. If you encounter authentication issues:
   - Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to a valid service account key file
   - Verify your project ID and location in `.env`
   - Check that the service account has the necessary permissions (`roles/aiplatform.user` and `roles/storage.admin`)
   - Ensure the Vertex AI API is enabled

2. If you get permission errors when using gcloud commands:
   - Service accounts have minimal permissions by design (principle of least privilege)
   - For administrative tasks like listing service accounts, use your personal Google account: `gcloud auth login`
   - The service account should only be used for application runtime operations
   - If you need to manage service accounts, use the Google Cloud Console or your personal authenticated account

3. If deployment fails:
   - Check the staging bucket exists and is accessible
   - Verify all required environment variables are set
   - Ensure you have the necessary permissions in your Google Cloud project

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your chosen license]
