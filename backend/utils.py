from functools import cache
import re
import requests
import sqlite3

import anthropic
from dotenv import load_dotenv

from commands.db_promotions_tostring import promotions_tostring
from commands.db_session_tostring import session_tostring

load_dotenv()

@cache
def _anthropic_client():
    client = anthropic.Anthropic()
    return client

def session_to_prompt(session_id, directive=None, test=False):
    session_str = session_tostring(session_id).strip()
    promotion_str = promotions_tostring(session_id).strip()

    prompt_str = f'''You will be given the browsing and mouse position data (recorded each second) from the user of a website.\nIn the <t> tag will be the text of the element they are hovering over at that time, or the tag of the element itself if there is no text.\n\n<browsing_data>\n{session_str}\n</browsing_data>\n\n'''
    prompt_str += f'''You will now be given a list of possible promotions from the creator of the website. Some will have specific discount parameters and others will have discount ranges.\n\n{promotion_str}'''
    if directive:
        prompt_str += f"\n\n{directive}"

    if test:
        print(prompt_str)
        return
    else:
        return prompt_str

SUMMARY_DIRECTIVE = "In under 140 characters, summarize what the user is trying to do on this website. Use as much of the data as possible to make your decision. Bias towards the LATEST POSSIBLE data because it is the most recent."
PROMOTION_DIRECTIVE = "Use all of the available browsing data, with a bias towards the LATEST POSSIBLE because it is the most recent. If there is a promotion that fits the user's browsing activity, output that promotion's ID EXACTLY and nothing else. If there is a range provided, select a discount within the range that you predict will be most effective for this specific user. Be very selective and only choose one if the user shows some intent that makes the promotion relevant for them. If not, output 'no promotion' and nothing else."
DEFAULT_SYSTEM_PROMPT = "You are an expert in psychology and consumer behavior."
def prompt_claude_session_context(session_id, directive=PROMOTION_DIRECTIVE):
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

def pagevisit_to_root_domain(data):
    page_url = data['pageURL']
    # Extract the root domain using a regular expression
    match = re.search(r'(?<=://)(?:www\.)?([^/?:]+)', page_url)
    if match:
        root_domain = match.group(1).split('.')[-2] + '.' + match.group(1).split('.')[-1]
    else:
        return None
    return root_domain

def promotion_id_to_dict(promotion_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('backend/db/app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM app_promotions WHERE id = ?', (promotion_id,))
    promotion = cursor.fetchone()

    conn.close()

    # Convert the promotion tuple to a dictionary
    promotion_dict = dict(zip([description[0] for description in cursor.description], promotion))

    return promotion_dict

def promotion_html_template(discount, title, description, discount_code):
    return f'''
    <div id="impulse-promotion" style="position:fixed; top:0; left:0; width:100%; height:100%; background-color:rgba(0,0,0,0.5); display:flex; justify-content:center; align-items:center; z-index: 9999;">
        <div style="position:relative; width:50%; max-width:600px; padding:20px; background-color:white; box-shadow:0 4px 6px rgba(0,0,0,0.25); text-align:center;">
            <div style="position:absolute; top:10px; right:10px; cursor:pointer;" onclick="this.parentElement.parentElement.style.display='none';">X</div>
            <div style="font-size:24px; font-weight:bold; margin-bottom:10px;">{discount}</div>
            <div style="font-size:20px; font-weight:bold; margin-bottom:10px;">{title}</div>
            <div style="font-size:16px; margin-bottom:10px;">{description}</div>
            <div style="font-size:20px; font-weight:bold;">{discount_code}</div>
        </div>
    </div>
    '''