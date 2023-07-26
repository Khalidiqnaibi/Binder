const {sendpythonmessage} = window.electron;


const chatLog = document.getElementById('chat-log');
const inputField = document.getElementById('input-field');
const sendButton = document.getElementById('send-button');


// Handle messages from Python script
window.electron.pythonsay((message) => {
  say(message)
});

function logAdd(txt) {
  const logEntry = document.createElement('p');
  logEntry.textContent = txt;
  chatLog.appendChild(logEntry);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function kprint(txt) {
  logAdd(`ASH: ${txt}`);
}

sendButton.addEventListener('click', () => {
  const message = inputField.value.trim();
  inputField.value = '';
  logAdd(`User: ${message}`);
  if (message !== '') {
    window.electron.sendpythonmessage(message);
  } 
});

// Call the "add_input" function when the Enter key is pressed in the input field
inputField.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    sendButton.click();
  }
});

function say(txt) {
  //const utterance = new SpeechSynthesisUtterance(txt);
  //speechSynthesis.speak(utterance);
  kprint(txt);
}

// Initial log entries
logAdd('Ash is up!');