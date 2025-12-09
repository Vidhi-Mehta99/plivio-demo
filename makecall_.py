import os
import plivo
from plivo import plivoxml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Plivo client with environment variables
client = plivo.RestClient(
    auth_id=os.getenv('PLIVO_AUTH_ID'),
    auth_token=os.getenv('PLIVO_AUTH_TOKEN')
)

response = client.calls.create(
    from_=os.getenv('PLIVO_NUMBER'),
    to_=os.getenv('SECONDARY_NUMBER'),
    answer_url=os.getenv('BASE_URL') + '/assistant/',
    answer_method='POST',
)
print(response)