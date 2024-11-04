from random import choices
from flask import render_template, request, jsonify, Response, redirect, url_for

from app import app, db, socketio, MODEL_NAME, SYSTEM_PROMPT
from model import Model
from db import db, Message, Session, Prompt
from utils import process_message


MODEL = None
MODEL_NAME = MODEL_NAME
SYSTEM_PROMPT = SYSTEM_PROMPT


def load_model():
    global MODEL
    if not MODEL:
        print("Loading model")
        MODEL = Model(MODEL_NAME, SYSTEM_PROMPT)
    print("Model is running")
    return

@socketio.on('send-message')
def handle_message(message):
    session_id = message['session_id']
    actor = message['actor']
    content = message['content']
    
    # Create a new message instance
    new_message = Message(session_id=session_id, actor=actor, content=content)
    db.session.add(new_message)
    db.session.commit()
    # # Emit the message to the room
    # socketio.emit('receive_message', {'message': message_content}, room=room)


@app.route('/')
def home():
    sessions = db.session.execute(db.select(Session)).all()
    prompt_id_names = db.session.execute(db.select(Prompt.id, Prompt.name).filter_by(hidden=False)).all()
    return render_template('index.html', sessions=sessions, prompt_id_names=prompt_id_names)

@app.route('/get_messages/<session_id>', methods=['GET'])
def get_messages(session_id):
    messages = db.session.execute(db.select(Message).filter_by(session_id=session_id)).all()
    return {'messages': [{'actor': msg[0].actor, 'content': msg[0].content, 'timestamp': msg[0].timestamp} for msg in messages]}

@app.route('/get_prompt/<prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    prompt = db.session.execute(db.select(Prompt).filter_by(id=prompt_id)).first()[0]
    return {'id': prompt.id, 'name': prompt.name, 'content': prompt.content}

@app.route('/create-session', methods=["POST"])
def create_session():
    if request.method == "POST":
        data = request.form
        load_model()
        
        session_name = data.get('name')
        new_prompt_name = data.get('prompt_name')
        new_prompt_content = data.get('prompt')

        if session_name == "":
            session_name = "Unnamed Session"
        if new_prompt_name == "":
            if new_prompt_content != "":
                if len(new_prompt_content) < 13:
                    new_prompt_name = new_prompt_content
                else:
                    new_prompt_name = new_prompt_content[:10] + "..."
            else:
                new_prompt_name = f"Prompt-{"".join(choices("0123456789", k=5))}"
        
        if new_prompt_content == "":
            new_prompt_content = SYSTEM_PROMPT

        prompt = db.session.execute(db.select(Prompt).filter_by(name=new_prompt_name)).first()
        if not prompt:
            prompt = Prompt(name=new_prompt_name, content=new_prompt_content, hidden=False)
            db.session.add(prompt)
            db.session.commit()
        elif prompt:
            prompt = prompt[0]
            if  prompt.content != new_prompt_content:
                prompt.content = new_prompt_content
                db.session.commit()
                print(f"Log: prompt updated")
        
        session_id = MODEL.new_session(prompt.content)
        new_session = Session(session_id=session_id, name=session_name, prompt_name=prompt.name)
        db.session.add(new_session)
        db.session.commit()

        return redirect(url_for("chat", session_id=session_id))
    return redirect("/404")


@app.route('/session/<session_id>')
def chat(session_id):
    session =  db.session.execute(db.select(Session).filter_by(session_id=session_id)).first()
    if not session:
        return redirect("/404")
    load_model()
    MODEL.load_session(session_id)
    return render_template('chat.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    result_messages = process_message(data)
    return jsonify(result_messages)

@app.route('/remove-session', methods=['POST'])
def remove_session():
    data = request.json
    session_id = data["session_id"]
    session = db.session.execute(db.select(Session).filter_by(session_id=session_id)).first()
    
    if session:
        db.session.delete(session[0])
        [db.session.delete(msg[0]) for msg in db.session.execute(db.select(Message).filter_by(session_id=session_id)).all()]
        db.session.commit()
    
    sessions = db.session.execute(db.select(Session)).all()
    return render_template('sessions.html', sessions=sessions)
    
@app.route('/remove-prompt', methods=['POST'])
def remove_prompt():
    data = request.json
    prompt_id = data["prompt_id"]
    prompt = db.session.execute(db.select(Prompt).filter_by(id=prompt_id)).first()
    
    if prompt:
        # db.session.delete(prompt[0])
        prompt[0].hidden = True
        db.session.commit()
    return redirect(url_for('home'))


def generate_stream(message):
    md = message['content']
    load_model()
    yield "2:"
    yield from MODEL.stream(md)

@app.route('/api/data-stream', methods=['POST'])
def receive_data():
    # Process the incoming data
    message = request.json
    return Response(generate_stream(message), content_type='text/event-stream')


@app.route('/reload-model', methods=['POST'])
def reload_model():
    return jsonify({'status': 'success'})
