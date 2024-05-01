from constants import initialize_command
initialize_command()

from backend.postgres.db_utils import _db_session
from backend.postgres.schema import Promotions

# From a promotion id, extract its information into a string suitable for an LLM prompt.
def ai_promotion_tostring(promotion_id, test=False):
    # Connect to the PostgreSQL database
    session = _db_session()

    # Query the database for the promotion
    p = session.query(Promotions).filter(Promotions.id == promotion_id).first()
    
    if p: # if promotion exists
        user_impulse_id = p.impulse_user_id
        session.close()
    elif not p.is_ai_generated:
        session.close()
        return ""
    else:
        session.close()
        return ""

    promotion_string = ""
    promotion_string += f"<promotion id={p.id}>\n"
    is_ai_generated = p.is_ai_generated
    if is_ai_generated:
        promotion_string += f"Description of this promotion: {p.ai_description}\n"
        if p.ai_discount_dollars_min: # this means the range is in dollars
            promotion_string += f"Range of possible discount in USD: from {p.ai_discount_dollars_min} to {p.ai_discount_dollars_max}\n"
        else: # range in percent
            promotion_string += f"Range of possible discount in percent off: from {p.ai_discount_percent_min} to {p.ai_discount_percent_max}\n"
    else:
        promotion_string += f"Title of the promotion: {p.display_title}\n"
        promotion_string += f"Description of the promotion: {p.display_description}\n"
        if p.discount_dollars: # dollars
            promotion_string += f"Discount in USD: {p.discount_dollars}\n"
        else:
            promotion_string += f"Discount in percent off: {p.discount_percent}\n"
    promotion_string += "</promotion>\n"

    if test:
        print(promotion_string)
        return
    else:
        return promotion_string