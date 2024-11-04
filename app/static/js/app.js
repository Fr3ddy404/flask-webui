const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatContainer = document.getElementById('chat-container');
var socket = io();
const session_id = window.location.href.split("/").pop();;

fetch(`/get_messages/${session_id}`)
.then(response => response.json())
.then(data => {
    data.messages.forEach(msg => {
        addMessage(msg);
    });
});

function addMessage(message) {
    let messageElement = null;
    if (!message.element) {
        messageElement = document.createElement('div');
        messageElement.setAttribute("is-selected", "false");
        messageElement.classList.add('chat-bubble');
        switch (message.actor) {
            case 0:
                messageElement.classList.add('system-bubble');
                break;
            case 1:
                messageElement.classList.add('user-bubble');
                break;
            case 2:
                messageElement.classList.add('incoming-bubble');
                break;
            default:
                throw `Exception: unknwon actor code: ${message.actor}`;
          }
          chatContainer.appendChild(messageElement);
    } else {
        messageElement = message.element;
    }
    messageElement.setAttribute("data-markdown", `${message.content}`);
    messageElement.innerHTML = `<input id="checkbox" type="checkbox" class="message-checkbox" checked>${formatMessage(message.content)}`;
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageElement;
}

function toggleSpoiler(element) {
    element.classList.toggle('revealed');
}

function splitOnFirstOccurrence(str, char) {
    // Split the string on the character
    const parts = str.split(char);
    // Check if there are at least two parts
    if (parts.length < 2) {
        return parts; // If not, return the parts as is
    }

    // Join the first part with the character and return the result
    return [parts[0], parts.slice(1).join(char)];
}


async function fetchDataStream(url, send_message) {
    try {
      const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"content": send_message.content, "actor": send_message.actor})
        })
  
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let message = null;
      let done = false;
      let result = '';
      let id = '';
      
      const { value, done: streamDone } = await reader.read();
      done = streamDone;
      result = decoder.decode(value, { stream: !done });
      result = splitOnFirstOccurrence(result, ':');
      actor = result[0];

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        if (value)
            result = decoder.decode(value, { stream: !done });
            result = splitOnFirstOccurrence(result, ':');
            id = result[0]
            break ;
      }
      message = {'id': id, 'content': '', 'actor': parseInt(actor, 10), "element": null};
      if (result[1] != '') {    
        message.content += result[1];
        message.element = addMessage(message);
      }
      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        if (value) {
            result = decoder.decode(value, { stream: !done });
            message.content += result;
            if (!message.element) {
                message.element = addMessage(message);
            } else {
                addMessage(message);
            }

        }
      }
      const messageJSON = {"session_id": session_id, "content": message.content, "actor": message.actor};
      socket.emit('send-message', messageJSON);
      console.log("Stream complete");
    } catch (error) {
      console.error("Error fetching data stream:", error);
    }
  }


sendButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        messageInput.value = '';
        const messageJSON = {"session_id": session_id, "content": message, "actor": 1};
        socket.emit('send-message', messageJSON);
        addMessage(messageJSON);
        fetchDataStream("/api/data-stream", messageJSON)
    }
});


messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendButton.click();
    }
});


function formatMessage(message) {
    message = marked.parse(message);
    // Parse the HTML string into a DOM object
    const parser = new DOMParser();
    const doc = parser.parseFromString(message, 'text/html');

    // Define regex patterns to match content inside square brackets
    
    // match empty brackets
    //const pattern1 = /\[([\t\f\v\ ]*)\]/g;
    
    const pattern2 = /\[([^\[\]\n]+)\]/g;
    
    // Function to replace text nodes matching a pattern
    function replaceTextNodes(node, pattern, replacement) {
        if (node.innerHTML) {
            node.innerHTML = node.innerHTML.replace(pattern, replacement);
            node.childNodes.forEach(node => replaceTextNodes(node, pattern, replacement));
        }
    }
    
    //replaceTextNodes(doc.body, pattern1, (match, p1) => `['${p1}']`);
    replaceTextNodes(doc.body, pattern2, (match, p1) => `<span class="spoiler" onclick="toggleSpoiler(this)">${p1}</span>`);
    message = doc.body.innerHTML;
    return message;
}
