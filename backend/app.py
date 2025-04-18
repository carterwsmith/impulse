from datetime import datetime
import requests
import threading
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy import func, desc, Integer
from sqlalchemy.orm import joinedload

from constants import ACTIVE_SESSION_TIMEOUT_MINUTES, SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS
from commands.db_get_user_image_urls import get_user_image_urls
from utils import pagevisit_to_root_domain, prompt_claude_session_context, promotion_id_to_dict, promotion_html_template, auth_user_id_to_promotion_dict_list, impulse_user_id_to_sessions_dict_list, auth_user_id_to_impulse_user_dict, url_to_root_domain, does_root_domain_exist, prompt_claude_promotion_context
from postgres.db_utils import _db_session, get_user_row
from postgres.schema import ImpulseUser, ImpulseSessions, PageVisits, MouseMovements, LLMResponses, Promotions, AuthUser

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_active_sessions(timeout_minutes=ACTIVE_SESSION_TIMEOUT_MINUTES):
    with _db_session() as session:

        now_ms = int(time.time() * 1000)
        one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
        socketio_interval_ago = now_ms - (SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS * 1000)
        
        active_sessions = session.query(MouseMovements.session_id).filter(
            MouseMovements.recorded_at > socketio_interval_ago,
            MouseMovements.session_id.in_(
                session.query(MouseMovements.session_id).group_by(MouseMovements.session_id).having(
                    func.min(MouseMovements.recorded_at) < socketio_interval_ago
                )
            ),
            MouseMovements.session_id.in_(
                session.query(ImpulseSessions.id).join(Promotions, ImpulseSessions.impulse_user_id == Promotions.impulse_user_id).filter(Promotions.is_active == True)
            ),
            MouseMovements.session_id.in_(
                session.query(ImpulseSessions.id).join(ImpulseUser, ImpulseSessions.impulse_user_id == ImpulseUser.id).filter(
                    session.query(func.count(LLMResponses.id).label('count')).filter(
                        LLMResponses.session_id == ImpulseSessions.id,
                        LLMResponses.is_emitted == True
                    ).scalar_subquery() < ImpulseUser.max_popups_per_session
                )
            )
        ).distinct().all()

        session.close()

    return [session[0] for session in active_sessions]

def prompt_claude_and_store_response(session_id, promotion=True):
    response = prompt_claude_session_context(session_id)
    timestamp = int(time.time())
    if promotion:
        if response.id is None:
            # generate placeholder html, desired behavior is no popup
            promotion_html = "no promotion"
        else:
            try:
                promotion_id_int = response.id
                promotion_dict = promotion_id_to_dict(promotion_id_int)
                promotion_ai_bool = int(promotion_dict["is_ai_generated"])
                if promotion_ai_bool:
                    # handle ai generating html logic here
                    try:
                        ai_promotion_obj = prompt_claude_promotion_context(session_id, promotion_id_int)
                    except Exception as e:
                        raise ValueError("Error while generating ai promotion content: {}".format(e))

                    discount_num = None
                    if ai_promotion_obj.discount % 1 == 0:
                        discount_num = int(ai_promotion_obj.discount)
                    elif promotion_dict['ai_discount_dollars_min']:
                        discount_num = "{:.2f}".format(ai_promotion_obj.discount)
                    else:
                        discount_num = ai_promotion_obj.discount
                    discount_var = f"{discount_num}% OFF" if promotion_dict['ai_discount_percent_min'] else f"${discount_num} OFF"
                    discountcode_var = promotion_dict["discount_code"] if promotion_dict["discount_code"] else ""
                    promotion_html = promotion_html_template(
                        discount_var, 
                        ai_promotion_obj.title, 
                        ai_promotion_obj.description, 
                        discount_code=discountcode_var,
                    )
                else:
                    # non ai generated html logic
                    discount_var = f"{int(promotion_dict['discount_percent']) if promotion_dict['discount_percent'] % 1 == 0 else promotion_dict['discount_percent']}% OFF" if promotion_dict['discount_percent'] else f"${int(promotion_dict['discount_dollars']) if promotion_dict['discount_dollars'] % 1 == 0 else "{:.2f}".format(promotion_dict['discount_dollars'])} OFF"
                    discountcode_var = promotion_dict["discount_code"] if promotion_dict["discount_code"] else ""

                    promotion_html = promotion_html_template(
                        discount_var,
                        promotion_dict["display_title"],
                        promotion_dict["display_description"],
                        discountcode_var,
                    )
            except:
                raise ValueError("Error while generating html")

    with _db_session() as session:
        llm_response = LLMResponses(session_id=session_id, response=response.id, recorded_at=timestamp, is_emitted=False, response_html=promotion_html)
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
    with _db_session() as session:

        # if no pagevisits (should just be during onboarding), do not update
        pagevisits_count = session.query(PageVisits).filter(PageVisits.session_id == session_id).count()
        if pagevisits_count == 0:
            session.close()
            return False

        now_ms = int(time.time() * 1000)
        one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
        last_position = session.query(MouseMovements.position_x, MouseMovements.position_y).filter(MouseMovements.session_id == session_id, MouseMovements.recorded_at > one_minute_ago).order_by(MouseMovements.recorded_at).first()
        has_mouse_movements = session.query(MouseMovements).filter(MouseMovements.session_id == session_id).count() > 0
        session.close()
    return (not last_position and not has_mouse_movements) or last_position[0] != new_x or last_position[1] != new_y

@socketio.on('mouseUpdate')
def handle_mouse_update(data):
    if should_log_mouse_update(data['session_id'], data['mousePos']['x'], data['mousePos']['y']):
        with _db_session() as session:
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

onboard_domain_set = set()
@socketio.on('pageVisit')
def handle_page_visit(data):
    with _db_session() as session:
    
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
                # assume onboarding
                if extracted_root_domain not in onboard_domain_set:
                    onboard_domain_set.add(extracted_root_domain)
                    session.close()
                    return

                # THIS IS JUST FOR TESTING!!!!! USES ADMIN USER ID AND SHOULD BE CHANGED!!!!
                #
                # If no user_id is found for the domain, insert with user_id 1
                # new_session = ImpulseSessions(id=data['session_id'], impulse_user_id=1)
                # session.add(new_session)
                # session.commit()

        new_page_visit = PageVisits(session_id=data['session_id'], pagevisit_token=data['pageVisitToken'], page_path=data['pagePath'], start_time=data['startTime'], end_time=None)
        session.add(new_page_visit)
        session.commit()
        session.close()

        emit('loadImagesComplete', get_user_image_urls(data['session_id']))

@socketio.on('pageVisitEnd')
def handle_page_visit_end(data):
    with _db_session() as session:
        page_visit = session.query(PageVisits).filter(PageVisits.pagevisit_token == data['pageVisitToken']).first()
        if page_visit:
            page_visit.end_time = data['endTime']
            session.commit()
            session.close()

@app.route('/promotions/get/user/<int:user_id>', methods=['GET'])
def get_user_promotions(user_id):
    promotion_dict_list = auth_user_id_to_promotion_dict_list(user_id)
    return jsonify(promotion_dict_list)

@app.route('/promotions/update/<int:promotion_id>', methods=['POST'])
def update_promotion(promotion_id):
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
    ]
    # If the promotion is ai generated, null all the non-ai keys, otherwise null the ai key
    if "is_ai_generated" in request_json:
        if request_json["is_ai_generated"]:
            for key in non_ai_keys:
                request_json[key] = None
        else:
            for key in ai_keys:
                request_json[key] = None

    with _db_session() as session:
        promotion = session.query(Promotions).filter(Promotions.id == promotion_id).first()
        if promotion:
            data = request_json
            for key, value in data.items():
                try:
                    setattr(promotion, key, value)
                except Exception as e:
                    session.rollback()
                    session.close()
                    return jsonify({'error': str(e)}), 500
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                session.close()
                return jsonify({'error': str(e)}), 500
        session.close()
    return jsonify({'success': True, 'promotion_id': promotion_id, 'values': data}), 200

@app.route('/promotions/delete/<int:promotion_id>', methods=['DELETE'])
def delete_promotion(promotion_id):
    with _db_session() as session:
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
    ]
    # If the promotion is ai generated, null all the non-ai keys, otherwise null the ai keys
    if request_json["is_ai_generated"]:
        for key in non_ai_keys:
            request_json[key] = None
    else:
        for key in ai_keys:
            request_json[key] = None

    # If non-required fields are 0 or '', set to None
    potentially_nullable_fields = [
        'image_url',
        'discount_percent',
        'discount_dollars',
        'ai_discount_percent_min',
        'ai_discount_percent_max',
        'ai_discount_dollars_min',
        'ai_discount_dollars_max',
    ]

    for field in potentially_nullable_fields:
        if request_json[field] == 0 or request_json[field] == '':
            request_json[field] = None

    with _db_session() as session:
        promotion = Promotions(**request_json)
        session.add(promotion)
        session.commit()
        session.close()
    return jsonify({'success': True}), 200

@app.route('/user_sessions/<int:user_id>', methods=['GET'])
def get_user_sessions(user_id):
    session_dict_list = impulse_user_id_to_sessions_dict_list(user_id)
    return jsonify(session_dict_list)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    try:
        user_dict = get_user_row(user_id)
        impulse_user_dict = auth_user_id_to_impulse_user_dict(user_id)
        # combine the dicts
        user_dict.update(impulse_user_dict)
        if user_dict is not None:
            return jsonify(user_dict), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/update/<int:user_id>', methods=['POST'])
def update(user_id):
    request_json = request.get_json()

    # data validation
    try:
        max_popups_per_session = int(request_json["max_popups_per_session"])
    except ValueError:
        return jsonify({'status': False, 'invalid_element': 'max_popups_per_session', 'message': 'Must be a number'}), 400
    if int(request_json["max_popups_per_session"]) <= 0:
        return jsonify({'status': False, 'invalid_element': 'max_popups_per_session', 'message': 'Must be greater than 0'}), 400

    with _db_session() as session:
        user = session.query(ImpulseUser).filter(ImpulseUser.id == user_id).first()

        if user:
            data = request_json
            for key, value in data.items():
                try:
                    setattr(user, key, value)
                except Exception as e:
                    session.rollback()
                    session.close()
                    return jsonify({'error': str(e)}), 500
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                session.close()
                return jsonify({'error': str(e)}), 500
        session.close()
    return jsonify({'success': True, 'user_id': user_id, 'values': data}), 200

@app.route('/user/onboard/<int:auth_id>', methods=['POST'])
def onboard(auth_id):
    try:
        request_json = request.get_json()
        user_domain = request_json['user_domain']
        try:
            # if user domain does not start with https:// or http://, add https://
            if not user_domain.startswith('https://') and not user_domain.startswith('http://'):
                user_domain = 'https://' + user_domain
            user_root_domain = url_to_root_domain(user_domain)
            # co.uk etc error handling can go here
            if not user_root_domain:
                return jsonify({'status': False, 'message': "Invalid domain"}), 400
            if does_root_domain_exist(user_root_domain):
                return jsonify({'status:': False, 'message': "Domain already registered"}), 400
        except Exception as e:
            return jsonify({'status': False, 'message': "Error parsing domain"}), 500

        # make a request to user_domain
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(user_domain, headers=headers)
        # return false if the response is not 200
        if response.status_code != 200:
            return jsonify({'status': False, 'message': 'Couldn\'t reach the domain'}), 400

        if user_root_domain in onboard_domain_set:
            onboard_domain_set.remove(user_root_domain)
            with _db_session() as session:
                session.query(ImpulseUser).filter(ImpulseUser.auth_id == auth_id).update({ImpulseUser.root_domain: user_root_domain, ImpulseUser.is_domain_configured: True})
                session.commit()
                session.close()

            return jsonify({'status': True, 'auth_id': auth_id, 'domain': user_domain, 'root_domain': user_root_domain}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

    return jsonify({'status': False, 'message': 'Onpulse.js not detected'}), 500

if __name__ == '__main__':
    socketio.start_background_task(prompt_active_sessions_background_task)
    socketio.run(app)