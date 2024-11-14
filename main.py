import json
import logging
from threading import Thread
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
    try:
        response = chat_completion_request(messages, tools=tools)
        log_to_apache_error_log(f"OpenAI Response: {json.dumps(response)}")
        if response and "choices" in response:
            assistant_message = response.choices[0].message["content"]
            return assistant_message
    except Exception as e:
        log_to_apache_error_log(f"OpenAI API Error: {str(e)}")

    return "I'm sorry, I couldn't process your request at the moment."

def handle_event_async(event):
    """
    Handles the Slack event asynchronously.
    """
    try:
        message_text = event["text"]
        message_text = message_text.replace(f"<@{BOT_USER_ID}>", "").strip()

        if message_text:
            # Process through OpenAI
            openai_response = process_openai_response(message_text)

            # Respond back in the same thread
            send_message_to_channel(openai_response, event["ts"])
    except Exception as e:
        log_to_apache_error_log(f"Error in async event handling: {str(e)}")

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
                # Immediately send 200 OK to Slack
                response_headers = [('Content-type', 'text/plain')]
                start_response('200 OK', response_headers)
                Thread(target=handle_event_async, args=(event,)).start()
                return [b"Event received"]

        # Default 200 OK response for other events
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
