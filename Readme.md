# Plivo Inbound Call Handler

A Flask application that calls the user

## Prerequisites

- Python 3.12 or higher
- Plivo account with valid credentials
- ngrok (for local testing with webhooks)

## Setup Instructions

1. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Mac
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Plivo Credentials**

   You can find Plivo credentials in your Plivo Console - (https://console.plivo.com/dashboard/).

4. **Set up ngrok (for local testing)**

   ```bash
   ngrok http 9000
   ```

   Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

5. **Configure Plivo Application**
   - Log in to your Plivo Console
   - Go to Voice > Applications
   - Create or edit an application
   - Set the Answer URL to: `https://your-ngrok-url/assistant`
   - Set the HTTP method to POST
   - Assign a Plivo number to this application

## Running the Application

1. **Start the Flask server**

   ```bash
   python ivr_server_.py
   ```

   The server will start on `http://localhost:9000`

2. **Make a test call**
   - Call your Plivo number
   - The application will answer and speak a greeting message

## API Endpoints

- `GET /` - Health check endpoint
- `POST /answer` - Webhook endpoint for handling inbound calls

## Troubleshooting

- **Webhook not receiving calls**: Ensure ngrok is running and the URL is correctly configured in Plivo Console
- **Authentication errors**: Verify your Auth ID and Auth Token
- **Port already in use**: Change the port in `ivr_server_.py` or kill the process using port 5000. Here, I changed it to 5001.

## Required Plivo Credentials

To run this application, you need:

- **Auth ID**: Your Plivo account authentication ID
- **Auth Token**: Your Plivo account authentication token

Both can be found in your [Plivo Console Dashboard](https://console.plivo.com/dashboard/).

### Sources

https://www.plivo.com/docs/voice/quickstart/python-quickstart#using-xml
https://www.plivo.com/blog/how-to-build-a-voice-controlled-ivr-in-python-using-flask-and-plivo/#expose-the-local-server-to-the-internet-using-ngrok
https://www.plivo.com/docs/voice/use-cases/receive-input#code-3
https://www.plivo.com/docs/voice/xml/speak/play-a-message
https://www.plivo.com/docs/voice/xml/play/play-music
