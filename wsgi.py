import json
import logging
import requests
logging.basicConfig(level=logging.INFO)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
BOT_USER_ID = "U080PEA1HAR"

def log_to_apache_error_log(message):
    logging.error(message)

def send_message_to_channel(text, thread_ts):
    payload = {"text": text, "thread_ts": thread_ts}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(SLACK_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    log_to_apache_error_log(f"Slack Webhook Response: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is: {response.text}")

def application(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        slack_event = json.loads(request_body)

        log_to_apache_error_log(f"Incoming Slack Event: {json.dumps(slack_event)}")

        if slack_event.get("type") == "url_verification":
            challenge = slack_event.get("challenge", "")
            response_headers = [('Content-type', 'application/json')]
            start_response('200 OK', response_headers)
            return [json.dumps({"challenge": challenge}).encode()]

        if slack_event.get("type") == "event_callback":
            event = slack_event.get("event", {})
            event_type = event.get("type")

            if event_type == "app_mention" and "text" in event:
                message_text = event["text"]
                message_text = message_text.replace(f"<@{BOT_USER_ID}>", "").strip()
                if message_text:
                    send_message_to_channel(message_text, event["ts"])

        response_headers = [('Content-type', 'text/plain')]
        start_response('200 OK', response_headers)
        return [b"Event received"]

    except Exception as e:
        log_to_apache_error_log(f"Error: {str(e)}")
        response_text = f"Error: {str(e)}"
        response_headers = [('Content-type', 'text/plain')]
        start_response('500 Internal Server Error', response_headers)
        return [response_text.encode()]
