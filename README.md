# Flask WebUI

A simple web interface with Markdown support built using Flask, designed to interact with Ollama models.

## Table of Contents
1. [Installation](#installation)
2. [Features](#features)
3. [Usage](#usage)
4. [License](#license)


## Features

- **💬 LLM Chat:** Chat with your Ollama instance.
- **📖 Markdown Support:** Chat messages are rendered in markdown.
- **📚 Multiple Conversations:** Have multiple conversation.
- **📜 Chat History:** Chat history is saved locally.
- **✍️ Custom Prompts:** Create and save custom prompts for you models.
- **⏩ Message Stream:** Messages are streamed by the llm.

## Installation

### Using pip
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install -r requirements.txt
```

### Using Nix

1. Follow the [Nix installation instructions](https://nixos.org/download/) to set up `nix`.

2. Enter the development shell from the flake.nix.

```bash
nix develop
```

## Usage

To run the application, navigate to the root directory and execute:

> [!WARNING]
> This command uses the Flask server in debug mode.


```bash
FLASK_APP=app/views FLASK_ENV=development flask --debug run
```

### Example

![demo of the Flask WebUI](/media/demo.gif)

### Select Models

By default a demo LLM is used. If you want to use your own models with Ollama you have to edit the app/app.py file.

```py
# set the model name to your model or leave it empty for the demo
MODEL_NAME = "" # "llama3.2:3b-instruct-q5_K_M"
```

### Markdown

You can use markdown commands in your messages.

![short markdown exaple](/media/short_markdown_example.png)

Answers by the model in markdown are rendered.

### Spoilers

![Example of a spoiler](/media/exapmle_spoiler.png)

Parts of the messages enclosed in `[` and `]` are hidden and can be made visble while hovering over it or by clicking on it. 


## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/). Feel free to modify and use it as you wish!