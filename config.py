from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get values from environment variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
BOT_USER_ID = os.getenv("BOT_USER_ID")
GPT_MODEL = os.getenv("GPT_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
