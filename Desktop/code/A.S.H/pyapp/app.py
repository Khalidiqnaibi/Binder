from flask import Flask, render_template, request, jsonify
from flaskwebgui import FlaskUI
import requests
import pymongo
from datetime import datetime
from ash_ai.ash import runn
import threading

user="khalid afif sami iqnaibi"

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["knowledge_db"]
inputlog=mydb["inputlog"]
chatlog=mydb['chatlog']
change =mydb['changes']
mcount=mydb["messagecount"]

app = Flask(__name__)
ui = FlaskUI(app)

messagecount=0
def mcntz():
    mcount.find_one_and_replace({"no":1}, {"no":1,"messagecount":0})
PAGE_SIZE = 10
mcntz()

def messagecount():
    c=mcount.find_one({"no":1})["messagecount"]
    return c

def messagecountP():
    l=messagecount()
    mcount.find_one_and_replace({"no":1},{"no":1,"messagecount":l+1})
    return l+1

@app.route('/')
def index():
    return render_template('index.html')

# Place the code from your 'runn' function inside the Flask route
@app.route('/api/ash', methods=['GET', 'POST'])
def run():
    # Retrieve the text data from the frontend
    #message = request.json['message']
    
    # Place your 'runn' function code here
    # ...
    # Modify the code as needed to process the 'text' variable and produce the desired result
    result="hi"
    
    # Return the result as JSON
    return jsonify({'result': result})

@app.route('/api/chatlog', methods=['GET', 'POST'])
def log():
    skipCount = messagecount()
    messages = chatlog.find().sort("time", 1).skip(skipCount).limit(PAGE_SIZE)
    c=[] 
    for i in messages:
        del i['_id']
        c.append(i)
    return jsonify(c)

@app.route('/api/lastmessage', methods=['GET', 'POST'])
def get_lastmessage():
    lastmessage = chatlog.find().sort('_id', -1)
    c = {"lastmessages": []}
    for i in lastmessage:
        if i['added by'] == user:
            break
        del i['_id']
        c["lastmessages"].append(i)
    return jsonify(c)

@app.route('/api/nextlog', methods=['GET', 'POST'])
def nlog():
    l=messagecount()
    mcount.find_one_and_replace({"no":1},{"no":1,"messagecount":l+PAGE_SIZE})
    c=requests.get("http://127.0.0.1:5000/api/chatlog").json()
    return jsonify(c)

@app.route('/api/insertinput', methods=['GET', 'POST'])
def get_insertinput():
    data = request.get_json()
    text = data['text']
    chatlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})
    inputlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})
    return "ok"

@app.route('/api/changelog', methods=['GET', 'POST'])
def get_log():# Retrieve the last document in the collection (assuming the documents are stored in chronological order)
    last_document = change.find().sort('_id', -1).limit(10)
    c=[]
    for i in last_document:
        del i['_id']
        c.append(i)
        v=messagecountP()
    return jsonify(c)

@app.route('/api/messagecount', methods=['GET', 'POST'])
def kk():
    return jsonify({"messagecount": messagecount()})

@app.route('/api/time', methods=['GET', 'POST'])
def time():
    return jsonify({"time": datetime.now().isoformat()})

@app.route('/api/messagecount+', methods=['GET', 'POST'])
def kkp():
    v=messagecountP()
    return jsonify({"messagecount": v})

@app.route('/api/mcntz', methods=['GET', 'POST'])
def mcountzero():
    data = request.get_json()
    text = data['text']
    mcntz()
    return "ok"


# Flag to control the background task loop
stop_flag = threading.Event()

def background_task():
    while not stop_flag.is_set():
        runn()

def stop_background_task():
    # Set the stop flag to terminate the background task loop
    stop_flag.set()

if __name__ == '__main__':
    # Start the background task in a separate thread
    bg_thread = threading.Thread(target=background_task)
    bg_thread.start()

    # Run the app using FlaskWebGUI
    app.run(debug=True)

    # Flask server has stopped, stop the background task
    stop_background_task()

