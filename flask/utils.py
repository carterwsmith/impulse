from functools import cache
import requests

import anthropic
from dotenv import load_dotenv

from commands.db_session_tostring import session_tostring

load_dotenv()

@cache
def _anthropic_client():
    client = anthropic.Anthropic()
    return client

def session_to_prompt(session_id, directive=None):
    session_str = session_tostring(session_id).strip()

    prompt_str = f'''You will be given the browsing and mouse position data (recorded each second) from the user of a website.\nIn the <t> tag will be the text of the element they are hovering over at that time, or the tag of the element itself if there is no text.\n\n<browsing_data>\n{session_str}\n</browsing_data>'''
    if directive:
        prompt_str += f"\n\n{directive}"

    return prompt_str

DEFAULT_DIRECTIVE = "In under 140 characters, summarize what the user is trying to do on this website."
DEFAULT_SYSTEM_PROMPT = "You are an expert in psychology and consumer behavior."
def prompt_claude_session_context(session_id, directive=DEFAULT_DIRECTIVE):
    client = _anthropic_client()
    prompt_contents = session_to_prompt(session_id, directive)

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.0,
        system=DEFAULT_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt_contents}
        ]
    )

    response = message.content[0].text
    return response