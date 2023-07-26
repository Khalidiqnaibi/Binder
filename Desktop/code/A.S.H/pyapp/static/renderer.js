
const user = "khalid afif sami iqnaibi";

var currentPage = 1;
var loading = false;
var messagecount,formattedTime;
var kh=false;
var lastmessage={"added by": "","text": '',"time": ""};

const chatLog = document.getElementById('chat-log');
const inputField = document.getElementById('input-field');
const sendButton = document.getElementById('send-button');



// Display chat log
mcntz();
displayChatLog();

function mcntz(){
  fetch('/api/mcntz', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ "text": "hi" })
 });
}

function insertinput(message){
  messagecountP();
  fetch('/api/insertinput', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ "text": message })
 });
}

function messagecountP(){
  fetch('/api/messagecount+')
  .then(response => response.json())
  .then(data => {
    // Process the data as needed
    messagecount=data["messagecount"];
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });
}

chatLog.addEventListener('scroll', handleScroll);

function log(txt){
  const logEntry = document.createElement('p');
  logEntry.textContent = txt;
  chatLog.appendChild(logEntry);
  chatLog.scrollTop = chatLog.scrollHeight;

}

function time(){
  fetch('/api/time')
  .then(response => response.json())
  .then(data => {
    // Process the data as needed
    formattedTime=data["time"];
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });
  return formattedTime
}

function kprint(txt) {
  formattedTime=time()
  log(`[${formattedTime}] A.S.H: ${txt}`)
  messagecountP();
}

function logAdd(txt) {
  formattedTime=time()
  log(`[${formattedTime}] ${user}: ${txt}`)
}

function displayChatLog() {
  loading = true;
  fetch('/api/chatlog')
  .then(response => response.json())
  .then(messages => {
    if (messages!==[]){
    messages.forEach((message) => {
      messagecountP();
      const formattedMessage = `[${message['time']}] ${message['added by']}: ${message.text}`;
      log(formattedMessage);
      lastmessage= message
    });
    fetchLastMessage();
    
    loading = false;
   }else{
    fetchLastMessage();
  }
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });
}

function displayNextLog() {
  loading = true;
  fetch('/api/nextlog')
  .then(response => response.json())
  .then(messages => {
    if (messages!==[]){
    //const shouldScrollToBottom = chatLog.scrollTop + chatLog.clientHeight === chatLog.scrollHeight;

    messages.forEach((message) => {
      messagecountP();
      const formattedMessage = `[${message['time']}] ${message['added by']}: ${message.text}`;
      appendMessageToChatLog(formattedMessage);
    });
    //if (shouldScrollToBottom) {
    //  scrollToBottom();
    //}

    loading = false;
   }
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });
}

function handleScroll() {
  const scrollTop = chatLog.scrollTop;
  const clientHeight = chatLog.clientHeight;

  if (scrollTop === 0 && !loading) {
    // User has scrolled to the top
    displayNextLog()
  }
}

function appendMessageToChatLog(message) {
  const newMessage = document.createElement('p');
  newMessage.classList.add('message');
  newMessage.textContent = message;
  chatLog.insertBefore(newMessage, chatLog.firstChild);
}

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

sendButton.addEventListener('click', () => {
  const message = inputField.value.trim();
  if (message !== '') {
    inputField.value = '';
    logAdd(message);
    
    // Send a POST request to the backend API
    insertinput(message);
  }
  else{
    inputField.value = '';
    logAdd(message);
  }
});
setInterval(fetchLastMessage, 2500);

// Call the "add_input" function when the Enter key is pressed in the input field
inputField.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    sendButton.click();
  }
});

function say(txt) {
  const utterance = new SpeechSynthesisUtterance(txt);
  speechSynthesis.speak(utterance);
  kprint(txt);
}


function fetchLastMessage() {
  fetch('/api/lastmessage')
  .then(response => response.json())
  .then(lm => {
    if (lm["lastmessages"]!==[]){
      if (
        lastmessage['added by'] !== lm['lastmessages'][0]['added by'] ||
        lastmessage['text'] !== lm['lastmessages'][0]['text'] ||
        lastmessage['time'] !== lm['lastmessages'][0]['time']
      ) {
        lm["lastmessages"].forEach((message) => {
          lastmessage = message;
          if (lastmessage["added by"]==="A.S.H"){
            say(lastmessage["text"]);
          }
          else if (lastmessage["added by"]!==user){
            log(lastmessage["text"]);
          }
        });
      }
    }else{
      log('Ash is up!');
    }
  })
  .catch(error => {
    console.error(error);
  });
}


