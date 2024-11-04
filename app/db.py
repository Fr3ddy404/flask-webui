from app import app, db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), nullable=False)
    actor = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Session(db.Model):
    session_id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    discription = db.Column(db.String(500))
    prompt_name = db.Column(db.String(32), nullable=False)

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    content = db.Column(db.String(500), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

with app.app_context():
    db.create_all()  # Setup code here
    try:
        default_prompt = Prompt(name="Default Prompt", content=SYSTEM_PROMPT)
        db.session.add(default_prompt)
        db.session.commit()
    except:
        pass