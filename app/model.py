import uuid
import time as t
from random import choice
from dataclasses import dataclass
from langchain_ollama import ChatOllama
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app import app
from db import db, Message

ACTOR_DICT = ["system", "human", "assistant"]

store = {}
with app.app_context():
    messages = db.session.execute(db.select(Message.id, Message.content, Message.actor, Message.session_id)).all()
    for message in messages:
        message_id = message[0]
        content = message[1]
        actor = message[2]
        session_id = message[3]
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        store[session_id].add_message(content)

  
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    
    # Get the existing history
    history = store[session_id]

    # Apply your filtering logic here
    filtered_messages = filter_messages(history.messages)
    
    # Create a new InMemoryChatMessageHistory with filtered messages
    filtered_history = InMemoryChatMessageHistory()
    for message in filtered_messages:
        filtered_history.add_message(message)
    
    return history# filtered_history

def get_last_k(messages: list, k=5) -> list:
    if len(messages) < k:
        return messages
    return messages#[-k:]

def filter_by_nr(messages, nr):
    for i in nr[::-1]:
        del messages[i]
    return messages

def filter_messages(messages: list) -> list:
    messages = get_last_k(messages)
    return messages

@dataclass
class ExampleChunk:
    id: str
    content: str    

class ExampleMessage:
    def __init__(self, content):
        self.id = f"run-{uuid.uuid4()}"
        self.content = content
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.content):
            raise StopIteration
        value = self.content[self.index]
        self.index += 1
        t.sleep(0.005)
        return ExampleChunk(self.id, value)

class ExampleModel:
    def __init__(self):
        self.messages = [
            "To create Spoilers, enclose the text in []. [This is a spoiler.]\n You can click on it to toggle visibility.",
            "To create a heading, use `#` followed by a space, like this: \n # This is a Heading. ",
            "For bold text, surround your text with two asterisks, like this: **Bold Text**.",
            "Italicize text using one underscore before and after the word, like this: _Italicized Text_.",
            "To make a list, start each item with `-`, `+`, or `*`, followed by a space, like this:\n - Item 1.",
            "For a blockquote, use the greater-than sign (`>`), like this: \n > This is a quote.",
            "Create a link by enclosing the URL in square brackets, followed by the text you want to display in parentheses, like this: [Visit our website](https://www.example.com)."
        ]
    
    def stream(self, *args,  **kwargs):
        msg = choice(self.messages)
        yield from ExampleMessage(msg)

class Model:
    def __init__(self, model, prompt):
        self.model = model
        if self.model == "":
            self.llm = None
            self.chat_llm = None
        else:
            self.llm = ChatOllama(model=self.model)
            self.chat_llm = None
        self.chain = None
        self.default_prompt = prompt
        self.prompt = None
        self.set_prompt()
        self.config = {"configurable": {"session_id": ""}}
        self.new_session()
        return

    def set_prompt(self, prompt=''):
        if prompt == '':
            prompt = self.default_prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        return

    def set_session_id(self, session_id=''):
        if session_id == '':
            session_id = str(uuid.uuid4())
        self.config["configurable"]["session_id"] = session_id
        return
        
    def new_session(self, prompt=''):
        
        self.set_prompt(prompt)
        self.set_session_id()
        if self.llm == None:
            self.chat_llm = ExampleModel()
        else:
            self.chain = self.prompt | self.llm
            self.chat_llm = RunnableWithMessageHistory(
                self.chain, 
                get_session_history, 
                input_messages_key="messages")
        return self.config["configurable"]["session_id"]

    def clear_conversation(self):
        return self.config["configurable"]["session_id"]


    def load_session(self, session_id):
        self.set_session_id(session_id)
        return

    def stream(self, msg):
        f = True
        for chunk in self.chat_llm.stream({"messages": msg}, config=self.config):
            if f:
                yield f"{chunk.id}:"
                f = False

            # last chunk.content is empty
            if chunk.content:
                yield f"{chunk.content}"