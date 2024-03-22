from commands.db_session_tostring import session_tostring

def session_to_prompt(session_id):
    session_str = session_tostring(session_id).strip()

    prompt_str = f'''You will be given the browsing and mouse position data (recorded each second) from the user of a website.\nIn the <t> tag will be the text of the element they are hovering over at that time, or the tag of the element itself if there is no text.\n\n<browsing_data>\n{session_str}\n</browsing_data>'''

    return prompt_str