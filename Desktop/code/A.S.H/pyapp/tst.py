import pymongo
from datetime import datetime
# Import module
import spacy
import wmi
from nltk.tokenize import word_tokenize, sent_tokenize

user="khalid afif sami iqnaibi"

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["knowledge_db"]
inputlog=mydb["inputlog"]
chatlog=mydb['chatlog']
mcount=mydb["messagecount"]

nlp = spacy.load('en_core_web_md')


def get_lastmessage():
    lastmessage = chatlog.find().sort('_id', -1).limit(1)
    c={"lastmessage":None}
    for i in lastmessage:
        del i['_id']
        c.update({"lastmessage":i})
    return jsonify(c)

def uinput():
    lastmessage = inputlog.find().sort('_id', -1).limit(1)
    c=[]
    for i in lastmessage:
        del i['_id']
        c.append(i)
    inputlog.delete_many({})
    return c[0]['text']



def insertinput(text):
    chatlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})
    inputlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})

            
def kprint(text):
    k={"added by":"ASH","text":text,"time":datetime.now()}
    chatlog.insert_one(k)
    
def addlog(text):
    k={"added by":f"{user}","text":text,"time":datetime.now()}
    inputlog.insert_one(k)
    chatlog.insert_one(k)
    
#def uinput(messege):
#    with inputlog.watch() as stream:
#        for change in stream:
#            # Check if the change event is an insert operation
#            if change['operationType'] == 'insert':
#                # Get the new document
#                new_document = change['fullDocument']
#                return new_document['text']
                
# Retrieve the last document in the collection (assuming the documents are stored in chronological order)
#last_document = change.find().sort('_id', -1).limit(20)
#for i in last_document:
#    print(i)

#mcount.insert_one({"no":4,"a":[]})

"""
# Initializing the wmi constructor
f = wmi.WMI()

nono=["python","python3","svchost","Lenovo","Creative Cloud","CCL","node","System","Intel","Memory","Registry"]

# Iterating through all the running processes
for process in f.Win32_Process():
    isnono=False
    for i in nono:
        if ( i in process.Name):
            isnono=True
    if not isnono:
        print(process.Name)"""
            
            
def get_pram(txt):
    def extract_id(txt):
        wrdid=word_tokenize(txt)
        for i in range(len(wrdid)):
            if wrdid[i] == "id":
                return wrdid[i+1]
    
    def extract_full_name(text):
        doc = nlp(text.title())

        full_name = ""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                full_name = ent.text.lower()
                break

        return full_name
    
    if "person with the id" in txt:
        return extract_id(txt)
    else:
        return extract_full_name(txt)
        



print(get_pram("khalid afif sami iqnaibi blood type"))


"what is the avrege life span of a dog"

"when was mika born"

"is khalid afif iqnaibis blood type A- ?"

"what is the scientific name of a sunflower"

"how much years until the extinction of the cat" 

"update the blood type of khalid afif sami iqnaibi to a+ from b+"
"update the breed of mika to ino from huski"
"update the price of my phone to 2500 from 2000"
"update the color of my phone to blue from red"
"update the color of khalid afif sami iqnaibi to black from white"

