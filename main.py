import json
import logging
from slack import send_message_to_channel
from open_ai import chat_completion_request
from pim import tools, system_prompt
from env_secrets import BOT_USER_ID

# Configure logging to log to Apache's error log
logging.basicConfig(level=logging.INFO)

def log_to_apache_error_log(message):
    """
    Logs a message to Apache's error log.
    """
    logging.error(message)

def process_openai_response(message_text):
    """
    Process the Slack message through OpenAI and return the assistant's response.
    """
    # Prepare messages for OpenAI
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message_text}
    ]
    # Log messages
    log_to_apache_error_log(f"Messages: {json.dumps(messages)}")

    # Call OpenAI
    response = chat_completion_request(messages, tools=tools)
    if response and "choices" in response:
        assistant_message = response.choices[0].message["content"]
        return assistant_message
    return "I'm sorry, I couldn't process your request at the moment."

def application(environ, start_response):
    """
    WSGI application to handle Slack events, respond in threads, and process via OpenAI.
    """
    try:
        # Read the incoming request
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        slack_event = json.loads(request_body)

        # Log incoming event
        log_to_apache_error_log(f"Incoming Slack Event: {json.dumps(slack_event)}")

        # Handle Slack URL verification
        if slack_event.get("type") == "url_verification":
            challenge = slack_event.get("challenge", "")
            response_headers = [('Content-type', 'application/json')]
            start_response('200 OK', response_headers)
            return [json.dumps({"challenge": challenge}).encode()]

        # Handle Slack event callbacks
        if slack_event.get("type") == "event_callback":
            event = slack_event.get("event", {})
            event_type = event.get("type")

            if event_type == "app_mention" and "text" in event:
                message_text = event["text"]
                message_text = message_text.replace(f"<@{BOT_USER_ID}>", "").strip()

                # Process through OpenAI
                if message_text:
                    openai_response = process_openai_response(message_text)

                    # Respond back in the same thread
                    send_message_to_channel(openai_response, event["ts"])

        # Send a generic "200 OK" response to Slack
        response_headers = [('Content-type', 'text/plain')]
        start_response('200 OK', response_headers)
        return [b"Event received"]

    except Exception as e:
        # Log errors to Apache error log
        log_to_apache_error_log(f"Error: {str(e)}")
        response_text = f"Error: {str(e)}"
        response_headers = [('Content-type', 'text/plain')]
        start_response('500 Internal Server Error', response_headers)
        return [response_text.encode()]
