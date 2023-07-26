import json 
import pymongo
from datetime import datetime


user="khalid afif sami iqnaibi"

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["knowledge_db"]
inputlog=mydb["inputlog"]
chatlog=mydb['chatlog']
mcount=mydb["messagecount"]
newes=mydb["new"]



#with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/actvdb.json','r') )as f:
#    pp=json.load(f)




c=newes.find_one({"new":"newactivity"})

print (c)
del c["_id"]
k={"intents":[]}
print(k)

for i in c:
    k["intents"].append({"tag":i,"patterns":[]})
print(k)
#
#
#print(k)

#f"is {user} 19 years old?"
#isq=["is","are"]
#for i in isq :
#    if i in qq:
#        tt=get_personinfo(qq)
        


#for i in pernew["intents"]:
#    ii=input (f"add a qustion to get {i['tag']}\n>> ")
#    if not ii == "" and not ii==" ":
#        i["patterns"].append(ii)


with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/actvdb.json','w')) as file:
    json.dump(k,file,indent=6)




