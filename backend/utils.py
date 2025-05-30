from functools import cache
import re
import requests

import anthropic
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel

from commands.db_ai_promotion_tostring import ai_promotion_tostring
from commands.db_promotions_tostring import promotions_tostring
from commands.db_session_tostring import session_tostring
from postgres.db_utils import _db_session
from postgres.schema import Promotions, ImpulseSessions, ImpulseUser, LLMResponses

load_dotenv()

@cache
def _anthropic_client():
    client = instructor.from_anthropic(anthropic.Anthropic())
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

class PromotionID(BaseModel):
    id: int | None

SUMMARY_DIRECTIVE = "In under 140 characters, summarize what the user is trying to do on this website. Use as much of the data as possible to make your decision. Bias towards the LATEST POSSIBLE data because it is the most recent."
PROMOTION_DIRECTIVE = "Use all of the available browsing data, with a bias towards the LATEST POSSIBLE because it is the most recent. If there is a promotion that fits the user's browsing activity, output that promotion's ID EXACTLY and nothing else. If there is a range provided, select a discount within the range that you predict will be most effective for this specific user. Be very selective and only choose one if the user shows some intent that makes the promotion relevant for them. If not, output None and nothing else."
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
        ],
        response_model=PromotionID
    )


    assert isinstance(message, PromotionID)
    #response = message.content[0].text
    #return response
    return message

def promotion_to_prompt(session_id, promotion_id, directive=None, test=False):
    session_str = session_tostring(session_id).strip()
    promotion_str = ai_promotion_tostring(promotion_id).strip()

    prompt_str = f'''You will be given the browsing and mouse position data (recorded each second) from the user of a website.\nIn the <t> tag will be the text of the element they are hovering over at that time, or the tag of the element itself if there is no text.\n\n<browsing_data>\n{session_str}\n</browsing_data>\n\n'''
    prompt_str += f'''You will now be given a concept of an e-commerce promotion from the creator of the website.\n\n{promotion_str}'''
    if directive:
        prompt_str += f"\n\n{directive}"

    if test:
        print(prompt_str)
        return
    else:
        return prompt_str

class GeneratedPromotion(BaseModel):
    discount: float
    title: str
    description: str

GENERATE_PROMOTION_DIRECTIVE = '''Given the activity of the user and the description of the promotion, create the following:

1. Determine what the value of the discount should be from within the provided range. Be discretionary, the amount should reflect how confident you are in the user's intent. Use round numbers that are appropriate for discounts if possible. Output ONLY THE NUMBER (no percent or dollar sign), and nothing else.
2. Generate a title (20 CHARACTERS MAX) for the promotion that will appear in a popup in large text. Do not mention specific product names, just general categories, do not make assumptions outside of the description. Output the title and nothing else.
3. Generate copy (50 CHARACTERS MAX) for the promotion that will appear in a popup underneath the title. Do not mention specific product names, just general categories, do not make assumptions outside of the description. Output the description and nothing else.'''
def prompt_claude_promotion_context(session_id, promotion_id, directive=GENERATE_PROMOTION_DIRECTIVE):
    client = _anthropic_client()
    prompt_contents = promotion_to_prompt(session_id, promotion_id, directive=directive)

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.0,
        system=DEFAULT_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt_contents}
        ],
        response_model=GeneratedPromotion
    )

    assert isinstance(message, GeneratedPromotion)
    #response = message.content[0].text
    #return response
    return message

def pagevisit_to_root_domain(data):
    page_url = data['pageURL']
    # Extract the root domain using a regular expression
    match = re.search(r'(?<=://)(?:www\.)?([^/?:]+)', page_url)
    if match:
        root_domain = match.group(1).split('.')[-2] + '.' + match.group(1).split('.')[-1]
    else:
        return None
    return root_domain

def url_to_root_domain(page_url):
    # Extract the root domain using a regular expression
    match = re.search(r'(?<=://)(?:www\.)?([^/?:]+)', page_url)
    if match:
        root_domain = match.group(1).split('.')[-2] + '.' + match.group(1).split('.')[-1]
    else:
        # If the URL doesn't start with 'http://' or 'https://', we assume it's already a root domain
        match = re.search(r'(?:www\.)?([^/?:]+)', page_url)
        if match:
            parts = match.group(1).split('.')
            if len(parts) >= 2: # set upper bound on this to throw err on co.uk and multi part domain endings
                root_domain = parts[-2] + '.' + parts[-1]
            else:
                return None  # Or handle differently if needed
        else:
            return None
    return root_domain

def does_root_domain_exist(root_domain):
    with _db_session() as session:
    
        user = session.query(ImpulseUser).filter(ImpulseUser.root_domain == root_domain).first()
        session.close()
    if user:
        return True
    else:
        return False

def promotion_id_to_dict(promotion_id):
    # Connect to the PostgreSQL database
    with _db_session() as session:

        promotion = session.query(Promotions).filter(Promotions.id == promotion_id).first()

        session.close()

    # Convert the promotion object to a dictionary
    promotion_dict = promotion.__dict__
    promotion_dict.pop('_sa_instance_state', None)


    ### SUMMARY STATS FOR DISPLAY IN TOOLTIP

    # number of LLMResponses where the promotion ID (cast as a string) is equal to the text of the 'response' column and is_emitted is True
    times_shown = session.query(LLMResponses).filter(LLMResponses.response == str(promotion_dict['id']), LLMResponses.is_emitted == True).count()
    promotion_dict['times_shown'] = times_shown

    return promotion_dict

def impulse_user_id_to_promotion_ids(impulse_user_id):
    # Connect to the PostgreSQL database
    with _db_session() as session:

        promotions = session.query(Promotions).filter(Promotions.impulse_user_id == impulse_user_id)

        session.close()

    if promotions:
        # Convert the promotion objects to a list of ids
        promotion_ids = [promotion.id for promotion in promotions]
        return promotion_ids
    else:
        return None

def auth_user_id_to_impulse_user_dict(auth_user_id):
    # Connect to the PostgreSQL database
    with _db_session() as session:
        impulse_user_obj = session.query(ImpulseUser).filter(ImpulseUser.auth_id == auth_user_id).first()
        impulse_user_dict = impulse_user_obj.__dict__
        impulse_user_dict.pop('_sa_instance_state', None)
        session.close()
    return impulse_user_dict

def auth_user_id_to_promotion_dict_list(auth_user_id):
    # Connect to the PostgreSQL database
    with _db_session() as session:

        impulse_user_obj = session.query(ImpulseUser).filter(ImpulseUser.auth_id == auth_user_id).first()

        session.close()

    if impulse_user_obj:
        impulse_user_id = impulse_user_obj.id
        user_promotion_ids = impulse_user_id_to_promotion_ids(impulse_user_id)
        if user_promotion_ids:
            output = []
            for i in sorted(user_promotion_ids):
                output.append(promotion_id_to_dict(i))
            return output
        else:
            return []
    else:
        return []

def impulse_user_id_to_sessions_dict_list(impulse_user_id):
    # Connect to the PostgreSQL database
    with _db_session() as session:
        user_sessions = session.query(ImpulseSessions).filter(ImpulseSessions.impulse_user_id == impulse_user_id)
        session.close()

    output = []
    if user_sessions:
        for s in user_sessions:
            s_dict = s.__dict__
            s_dict.pop('_sa_instance_state', None)
            output.append(s_dict)
        return output
    else:
        return []

def promotion_html_template(discount, title, description, discount_code, image_url="https://content.api.news/v3/images/bin/82b374759b87b7e45eb5dbb04157d7cc"):
    return '''<div id="impulse-promotion" onclick="if (event.target === this) { this.style.display = 'none'; }"
    style="position:fixed !important; top:0 !important; left:0 !important; width:100% !important; height:100% !important; background-color:rgba(0,0,0,0.5); display:flex; justify-content:center; align-items:center; z-index: 9999;">
    <div
      style="position:relative !important; width:50% !important; max-width:500px !important; min-width:300px; padding:20px 0 20px 0 !important; background-color:white !important; box-shadow:0 4px 6px rgba(0,0,0,0.25) !important; text-align:center !important; border-radius: 10px;">
      <div style="position:absolute; font-size:30px; top:5px; right:15px; cursor:pointer;"
        onclick="this.parentElement.parentElement.style.display='none';">&times;</div>
      <div>
        <div style="font-size:60px; font-weight:bold; margin-bottom:20px; font-family: 'Jost', sans-serif;">{discount}</div>
            <img src="{image_url}" style="width: 100%; max-height: 150px; padding-bottom: 10px; object-fit: cover;">
        <div style="font-size:20px; font-weight:bold; margin-bottom:10px; font-family: 'Jost', sans-serif;">{title}</div>
        <div style="font-size:16px; margin-bottom:10px; font-family: 'Jost', sans-serif;">{description}</div>
        <div style="font-size:20px; font-weight:bold; font-family: 'Jost', sans-serif;">{discount_code}</div>
      <div>
    </div>
  </div>
    '''.format(discount=discount, title=title, description=description, discount_code=discount_code, image_url=image_url).replace('\n', '')