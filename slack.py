import json
import requests
from env_secrets import SLACK_WEBHOOK_URL

def send_message_to_channel(text, thread_ts):
    payload = {"text": text, "thread_ts": thread_ts}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(SLACK_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError(f"Slack error {response.status_code}: {response.text}")
