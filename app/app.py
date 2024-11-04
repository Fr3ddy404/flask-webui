# run: FLASK_APP=views FLASK_ENV=development flask --debug run

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# set the model name to your model or leave it empty for the demo
MODEL_NAME = "" # "llama3.2:3b-instruct-q5_K_M"
SYSTEM_PROMPT = """You are a helpful assistant."""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///session.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)

db = SQLAlchemy(app)
