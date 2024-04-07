import sqlite3

# From a session UUID, extract the user and all active promotions to construct a string suitable for an LLM prompt.
def promotions_tostring(session_id, test=False):
    # Connect to the SQLite database
    conn = sqlite3.connect('backend/db/app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT django_user_id FROM app_sessions WHERE id = ?', (session_id,))
    django_user_id = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM app_promotions WHERE django_user_id = ?', (django_user_id,))
    promotions = cursor.fetchall()

    conn.close()

    promotion_string = ""
    for promotion_tuple in promotions:
        promotion_string += f"<promotion id={promotion_tuple[0]}>\n"
        is_ai_generated = promotion_tuple[11]
        if is_ai_generated:
            ai_columns = promotion_tuple[6:11]
            promotion_string += f"Description of this promotion's target audience: {ai_columns[0]}\n"
            if ai_columns[1]: # this means the range is in dollars
                promotion_string += f"Range of possible discount in USD: from {ai_columns[2]} to {ai_columns[1]}\n"
            else: # range in percent
                promotion_string += f"Range of possible discount in percent off: from {ai_columns[4]} to {ai_columns[3]}\n"
        else:
            nonai_columns = promotion_tuple[1:5] + tuple([promotion_tuple[12]])
            promotion_string += f"Title of the promotion: {nonai_columns[4]}\n"
            promotion_string += f"Description of the promotion: {nonai_columns[1]}\n"
            if nonai_columns[3]: # dollars
                promotion_string += f"Discount in USD: {nonai_columns[3]}\n"
            else:
                promotion_string += f"Discount in percent off: {nonai_columns[2]}\n"
        promotion_string += "</promotion>\n"

    if test:
        print(promotion_string)
        return
    else:
        return promotion_string