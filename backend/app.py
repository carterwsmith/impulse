from datetime import datetime
import threading
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy import func, desc, Integer
from sqlalchemy.orm import joinedload

from constants import ACTIVE_SESSION_TIMEOUT_MINUTES, SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS
from commands.db_get_user_image_urls import get_user_image_urls
from utils import pagevisit_to_root_domain, prompt_claude_session_context, promotion_id_to_dict, promotion_html_template, auth_user_id_to_promotion_dict_list, impulse_user_id_to_sessions_dict_list
from postgres.db_utils import _db_session
from postgres.schema import ImpulseUser, ImpulseSessions, PageVisits, MouseMovements, LLMResponses, Promotions

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_active_sessions(timeout_minutes=ACTIVE_SESSION_TIMEOUT_MINUTES):
    session = _db_session()

    now_ms = int(time.time() * 1000)
    one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
    socketio_interval_ago = now_ms - (SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS * 1000)
    
    active_sessions = session.query(MouseMovements.session_id).filter(
        MouseMovements.recorded_at > socketio_interval_ago,
        MouseMovements.session_id.in_(
            session.query(MouseMovements.session_id).group_by(MouseMovements.session_id).having(
                func.min(MouseMovements.recorded_at) < socketio_interval_ago
            )
        )
    ).distinct().all()

    session.close()

    return [session[0] for session in active_sessions]

def prompt_claude_and_store_response(session_id, promotion=True):
    response = prompt_claude_session_context(session_id)
    timestamp = int(time.time())
    if promotion:
        if 'no promotion' in response:
            # generate placeholder html, desired behavior is no popup
            promotion_html = "no promotion"
        else:
            try:
                promotion_id_int = int(response)
                promotion_dict = promotion_id_to_dict(promotion_id_int)
                promotion_ai_bool = int(promotion_dict["is_ai_generated"])
                if promotion_ai_bool:
                    # handle ai generating html logic here
                    promotion_html = promotion_html_template("_", "placeholder", "_", "_")
                else:
                    # non ai generated html logic
                    discount_var = f"{int(promotion_dict['discount_percent']) if promotion_dict['discount_percent'] % 1 == 0 else promotion_dict['discount_percent']}% OFF" if promotion_dict['discount_percent'] else f"${promotion_dict['discount_dollars']}"
                    discountcode_var = promotion_dict["discount_code"] if promotion_dict["discount_code"] else ""

                    promotion_html = promotion_html_template(
                        discount_var,
                        promotion_dict["display_title"],
                        promotion_dict["display_description"],
                        discountcode_var,
                    )
            except:
                raise ValueError("Error while generating html")

    session = _db_session()
    llm_response = LLMResponses(session_id=session_id, response=response, recorded_at=timestamp, is_emitted=False, response_html=promotion_html)
    session.add(llm_response)
    session.commit()
    session.close()
    
    return response, timestamp

def prompt_active_sessions_background_task():
    socketio.sleep(SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS)
    while True:
        active_sessions = get_active_sessions()
        #print(active_sessions)
        for session_id in active_sessions:
            response, timestamp = prompt_claude_and_store_response(session_id)
        socketio.sleep(SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS)

def should_log_mouse_update(session_id, new_x, new_y):
    session = _db_session()
    now_ms = int(time.time() * 1000)
    one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
    last_position = session.query(MouseMovements.position_x, MouseMovements.position_y).filter(MouseMovements.session_id == session_id, MouseMovements.recorded_at > one_minute_ago).order_by(MouseMovements.recorded_at).first()
    has_mouse_movements = session.query(MouseMovements).filter(MouseMovements.session_id == session_id).count() > 0
    session.close()
    return (not last_position and not has_mouse_movements) or last_position[0] != new_x or last_position[1] != new_y

@socketio.on('mouseUpdate')
def handle_mouse_update(data):
    if should_log_mouse_update(data['session_id'], data['mousePos']['x'], data['mousePos']['y']):
        session = _db_session()
        mouse_movement = MouseMovements(
            session_id=data['session_id'],
            pagevisit_token_id=data['pageVisitToken'],
            position_x=data['mousePos']['x'],
            position_y=data['mousePos']['y'],
            text_or_tag_hovered=data['hovered'],
            recorded_at=data['recordedAt']
        )
        session.add(mouse_movement)
        session.commit()

        # also check if there is a llmresponse that is not emitted
        llm_response = session.query(LLMResponses.response_html).filter(LLMResponses.is_emitted == False, LLMResponses.session_id == data['session_id']).order_by(LLMResponses.recorded_at.desc()).first()
        if llm_response:
            emit('llmResponse', llm_response[0])
            # Set the is_emitted of the most recent llmresponse for that session_id to TRUE
            session.query(LLMResponses).filter(LLMResponses.session_id == data['session_id']).update({LLMResponses.is_emitted: True})
            session.commit()
        session.close()

@socketio.on('pageVisit')
def handle_page_visit(data):
    session = _db_session()
    
    ## create session if needed
    # Check if the session exists
    session_exists = session.query(ImpulseSessions).filter(ImpulseSessions.id == data['session_id']).first()
    
    # If the session does not exist, create it
    if not session_exists:
        extracted_root_domain = pagevisit_to_root_domain(data)
        # probably need some error handling here too
        user_id = session.query(ImpulseUser.id).filter(ImpulseUser.root_domain.like('%' + extracted_root_domain + '%')).first()
        if user_id:
            new_session = ImpulseSessions(id=data['session_id'], impulse_user_id=user_id[0])
            session.add(new_session)
            session.commit()
        else:
            #
            # THIS IS JUST FOR TESTING!!!!! USES ADMIN USER ID AND SHOULD BE CHANGED!!!!
            #
            # If no user_id is found for the domain, insert with user_id 1
            new_session = ImpulseSessions(id=data['session_id'], impulse_user_id=1)
            session.add(new_session)
            session.commit()

    new_page_visit = PageVisits(session_id=data['session_id'], pagevisit_token=data['pageVisitToken'], page_path=data['pagePath'], start_time=data['startTime'], end_time=None)
    session.add(new_page_visit)
    session.commit()
    session.close()

    emit('loadImagesComplete', get_user_image_urls(data['session_id']))

@socketio.on('pageVisitEnd')
def handle_page_visit_end(data):
    session = _db_session()
    page_visit = session.query(PageVisits).filter(PageVisits.pagevisit_token == data['pageVisitToken']).first()
    if page_visit:
        page_visit.end_time = data['endTime']
        session.commit()
        session.close()

@app.route('/user_promotions/<int:user_id>', methods=['GET'])
def get_user_promotions(user_id):
    promotion_dict_list = auth_user_id_to_promotion_dict_list(user_id)
    return jsonify(promotion_dict_list)

@app.route('/promotions/update/<int:promotion_id>', methods=['POST'])
def update_promotion(promotion_id):
    session = _db_session()
    promotion = session.query(Promotions).filter(Promotions.id == promotion_id).first()
    if promotion:
        data = request.get_json()
        for key, value in data.items():
            try:
                setattr(promotion, key, value)
            except Exception as e:
                session.rollback()
                return jsonify({'error': str(e)}), 500
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 500
    session.close()
    return jsonify({'success': True, 'promotion_id': promotion_id, 'values': data}), 200

@app.route('/promotions/delete/<int:promotion_id>', methods=['DELETE'])
def delete_promotion(promotion_id):
    session = _db_session()
    promotion = session.query(Promotions).filter(Promotions.id == promotion_id).first()
    if promotion:
        session.delete(promotion)
        session.commit()
        session.close()
    return jsonify({'success': True, 'promotion_id_deleted': promotion_id}), 200

@app.route('/promotions/add', methods=['POST'])
def add_promotion():
    request_json = request.get_json()

    ai_keys = [
        "ai_description",
        "ai_discount_percent_min",
        "ai_discount_percent_max",
        "ai_discount_dollars_min",
        "ai_discount_dollars_max",
    ]
    non_ai_keys = [
        "image_url",
        "display_title",
        "display_description",
        "discount_percent",
        "discount_dollars",
        "discount_code",
    ]
    # If the promotion is ai generated, null all the non-ai keys, otherwise null the ai keys
    if request_json["is_ai_generated"]:
        for key in non_ai_keys:
            request_json[key] = None
    else:
        for key in ai_keys:
            request_json[key] = None

    session = _db_session()
    promotion = Promotions(**request_json)
    session.add(promotion)
    session.commit()
    session.close()
    return jsonify({'success': True}), 200

@app.route('/user_sessions/<int:user_id>', methods=['GET'])
def get_user_sessions(user_id):
    session_dict_list = impulse_user_id_to_sessions_dict_list(user_id)
    return jsonify(session_dict_list)

if __name__ == '__main__':
    socketio.start_background_task(prompt_active_sessions_background_task)
    socketio.run(app)