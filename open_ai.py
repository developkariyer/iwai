from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from env_secrets import GPT_MODEL, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
    )
    return response
