from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_users = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join():
    try_match(request.sid)

def try_match(user_sid):
    for partner_sid in waiting_users:
        if partner_sid != user_sid:
            waiting_users.remove(partner_sid)
            room = f'{partner_sid}-{user_sid}'
            join_room(room, sid=user_sid)
            join_room(room, sid=partner_sid)
            emit('match', room, room=partner_sid)
            emit('match', room, room=user_sid)
            return
    if user_sid not in waiting_users:
        waiting_users.append(user_sid)

@socketio.on('next')
def handle_next():
    # Leave all rooms
    sid = request.sid
    leave_user_from_rooms(sid)

    # Re-add partner to waiting list and try to match them
    partner_sid = remove_partner_from_room(sid)
    if partner_sid:
        try_match(partner_sid)

    try_match(sid)

def leave_user_from_rooms(sid):
    rooms = list(socketio.server.manager.rooms['/'].keys())
    for room in rooms:
        if sid in socketio.server.manager.rooms['/'][room]:
            leave_room(room, sid=sid)

def remove_partner_from_room(sid):
    for room, members in socketio.server.manager.rooms['/'].items():
        if sid in members:
            others = members - {sid}
            if others:
                partner_sid = list(others)[0]
                leave_room(room, sid=partner_sid)
                return partner_sid
    return None

@socketio.on('send_message')
def handle_message(message):
    for room, members in socketio.server.manager.rooms['/'].items():
        if request.sid in members:
            emit('receive_message', f'Partner: {message}', room=room, include_self=False)
            break

@socketio.on('leave')
def handle_leave():
    if request.sid in waiting_users:
        waiting_users.remove(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in waiting_users:
        waiting_users.remove(request.sid)
    # Handle partner cleanup
    partner_sid = remove_partner_from_room(request.sid)
    if partner_sid:
        try_match(partner_sid)

@socketio.on('offer')
def handle_offer(data):
    room = data['room']
    emit('offer', data['offer'], room=room, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    room = data['room']
    emit('answer', data['answer'], room=room, include_self=False)

@socketio.on('ice-candidate')
def handle_ice(data):
    room = data['room']
    emit('ice-candidate', data['candidate'], room=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    # socketio.run(app, port=5000, allow_unsafe_werkzeug=True)
