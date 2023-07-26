import random
import json
import pickle
import spacy
import numpy as np
import nltk
import string
import requests
import pyttsx3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import os
import pymongo
import webbrowser
import tkinter as tk
from tkinter import Image, Image, font,PhotoImage,scrolledtext
from googleapiclient.discovery import build
from datetime import timedelta,datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from nltk.classify import NaiveBayesClassifier
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import time


#Ash attempt num 4  

user="khalid afif sami iqnaibi"

load_dotenv()
YOU_API_KEY = os.getenv("YOU_API_KEY")    
W_API_KEY = os.getenv("W_API_KEY")

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["knowledge_db"]
people = mydb["people"]
activities= mydb["activities"]
actlogs=mydb['activities_logs']
changes=mydb["changes"]
organisms=mydb["organisms"]
known_things=mydb["specific_known_things"]
animals=mydb["animals"]
products=mydb["products"]
events=mydb['events']
Qs=mydb["questions"]
new=mydb["new"]
plants=mydb['plants']
relationships=mydb['relationships']
dairy=mydb["dairy"]
weather = mydb["weather"]
forecast = mydb["daily_forecast"]
inputlog=mydb["inputlog"]
chatlog=mydb['chatlog']
mcount=mydb["messagecount"]


class peopledb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newperson"})
        del c["_id"]
        self.newPerson=c
    def Add(self,catagory,value):
        person=self.newPerson
        person.update({catagory:value})
        people.insert_one(person)
        ch={"change":f"added a person with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
            person=people.find_one({param: val})
            return person

    def Update(self,param,val,catagory,newvalue):
        per=self.Get(param, val)
        ch={"change":f"updated actionlog with catagory: {catagory} at the value: {newvalue} for the person:{per['name']}, old values are: ({catagory},{per[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        per.update({catagory: newvalue})
        people.find_one_and_replace({param: val}, per)
        
    def Del(self,catagory,value):
        people.find_one_and_delete({catagory:value})
        ch={"change":f"deleted a person with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def UpdateNew(self,catagory,newvalue):
        newPerson=self.newPerson
        ch={"change":f"updated newPerson with the catagory: {catagory} at the value: {newPerson} for : (newPerson), old values are: ({catagory},{newPerson[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newPerson.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newPerson"},newPerson)

class activitiesdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newactivity"})
        del c["_id"]
        self.newAct=c
        
    def Add(self,catagory,value):
        act=self.newAct
        act.update({catagory:value})
        activities.insert_one(act)
        ch={"change":f"added new activity with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
            act=activities.find_one({param: val})
            return act

    def Del(self,catagory,value):
        activities.find_one_and_delete({catagory:value})
        ch={"change":f"deleted an activitie with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Update(self,param,val,catagory,newvalue):
        act=self.Get(param, val)
        ch={"change":f"updated activity with the catagory: {catagory} at the value: {newvalue}  for the activity: ({act['name']}),old values are: ({catagory},{act[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        act.update({catagory: newvalue})
        activities.find_one_and_replace({param: val}, act)
    
    def UpdateNew(self,catagory,newvalue):
        newAct=self.newAct
        ch={"change":f"updated newAct with the catagory: {catagory} at the value: {newvalue} for : (newAct), old values are: ({catagory},{newAct[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newAct.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newAct"},newAct)

class activitieslogsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newactivities_log"})
        del c["_id"]
        self.newActlog=c
        
    def addActlog(self,personid,date,activitieid):
        log=self.newActlog
        log['person id']=personid
        log['date']=date
        log['activitie id']=activitieid
        actlogs.insert_one(log)
        ch={"change":f"added new actionlog with person id: ({personid}) with activity id: ({activitieid})","time":datetime.now()}
        changes.insert_one(ch)

    def delActlog(self,personid,activityid):
        actlogs.find_one_and_delete({"person id": personid,"activity id": activityid})
        ch={"change":f"deleted an actlog with the person id: {personid} at the activity id: {activityid}","time":datetime.now()}
        changes.insert_one(ch)
    
    def addActLogwithdata(self,catagory,addedData):
        log=self.newActlog
        log.update({catagory:addedData})
        actlogs.insert_one(log)
        ch={"change":f"added new actionlog with the catagory: {catagory} at the value: {addedData}","time":datetime.now()}
        changes.insert_one(ch)
    
    def getactlog(self,personid,activityid):
            log=actlogs.find_one({"person id": personid,"activity id": activityid})
            return log

    def UpdateOneActlog(self,personid,activityid,catagory,newvalue):
        log=self.getactlog(personid,activityid)
        ch={"change":f"updated actionlog with the catagory: {catagory} at the value: {newvalue} for the activtylog: (person id :{personid},activity id:{activityid}),old values are: ({catagory},{log[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        log.update({catagory: newvalue})
        actlogs.find_one_and_replace({"person id": personid,"activity id": activityid}, log)
                
    def UpdatenewActlog(self,catagory,newvalue):
        newActlog=self.newActlog
        ch={"change":f"updated newActlog with the catagory: {catagory} at the value: {newvalue} for : (newActlog), old values are: ({catagory},{newActlog[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newActlog.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newActlog"},newActlog)

class organismsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"neworganism"})
        del c["_id"]
        self.newOrganism=c
        
    def Add(self,catagory,value):
        org=self.newOrganism
        org.update({catagory:value})
        organisms.insert_one(org)
        ch={"change":f"added an new organism with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Del(self,catagory,value):
        organisms.find_one_and_delete({catagory:value})
        ch={"change":f"deleted an organism with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
        organism=organisms.find_one({param: val})
        return organism

    def Update(self,param,val,catagory,newvalue):
        organism=self.Get(param, val)
        ch={"change":f"updated organisms with the catagory: {catagory} at the value: {newvalue} for the organism: ({organism['common name']}), old values are: ({catagory},{organism[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        organism.update({catagory: newvalue})
        organisms.find_one_and_replace({param: val}, per)

    def UpdateNew(self,catagory,newvalue):
        newOrganism=self.newOrganism
        ch={"change":f"updated newOrganism with the catagory: {catagory} at the value: {newvalue} for : (newOrganism), old values are: ({catagory},{newOrganism[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newOrganism.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newOrganism"},newOrganism)

class animalsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newanimal"})
        del c["_id"]
        self.newAnimal=c
    
    def Add(self,catagory,value):
        anml=self.newAnimal
        if catagory in["name"]:
            catagory="common name"
        else:
            pass
        anml.update({catagory:value})
        animals.insert_one(anml)
        ch={"change":f"added an new animal with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Del(self,catagory,value):
        animals.find_one_and_delete({catagory:value})
        ch={"change":f"deleted an animal with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
            organism=organisms.find_one({param: val})
            return organism
    
    def Update(self,param,val,catagory,newvalue):
        animal=self.Get(param, val)
        ch={"change":f"updated animals with the catagory: {catagory} at the value: {newvalue} for the animal: ({animal['common name']}), old values are: ({catagory},{animal[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        animal.update({catagory: newvalue})
        animals.find_one_and_replace({param: val}, animal)
        
    def UpdateNew(self,catagory,newvalue):
        newAnimal=self.newAnimal
        ch={"change":f"updated newAnimal with the catagory: {catagory} at the value: {newvalue} for : (newAnimal), old values are: ({catagory},{newAnimal[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newAnimal.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newAnimal"},newAnimal)
        
class plantsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newplant"})
        del c["_id"]
        self.newPlant=c

    def Add(self,catagory,value):
        anml=self.newPlant
        if catagory in["name"]:
            catagory="common name"
        else:
            pass
        anml.update({catagory:value})
        plants.insert_one(anml)
        ch={"change":f"added an plants with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
        organism=organisms.find_one({param: val})
        return organism
    
    def Update(self,param,val,catagory,newvalue):
        plant=self.Get(param, val)
        ch={"change":f"updated plants with the catagory: {catagory} at the value: {newvalue} for the plant: ({plant['common name']}), old values are: ({catagory},{animal[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        plant.update({catagory: newvalue})
        plants.find_one_and_replace({param: val}, plant)
        
    def Del(self,catagory,value):
        plants.find_one_and_delete({catagory:value})
        ch={"change":f"deleted a plant with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def UpdateNew(self,catagory,newvalue):
        newplant=self.newPlant
        ch={"change":f"updated newplant with the catagory: {catagory} at the value: {newvalue} for : (newplant), old values are: ({catagory},{newplant[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newplant.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newplant"},newplant)

class knownthingsdb():
    def __init__(self):
        self.TheBest="Khalid"
        
    def newknowns(self,fathercollction):
        if fathercollction == "animals":
            newknown=new.find_one({"new":"newknownAnimal"})
        elif fathercollction == "products":
            newknown=new.find_one({"new":"newknownProduct"})
        elif fathercollction == "plants":
            newknown=new.find_one({"new":"newknownPlants"})
        else:
            newknown=new.find_one({"new":"newknown"})
        
        del newknown["_id"]
        
        return newknown
    
    def getfather(self,fathername,dbname):
        father=(dbname.find_one({"name":fathername}))
        return father 
    
    def delKnown(self,catagory,value):
        known_things.find_one_and_delete({catagory:value})
        ch={"change":f"deleted the known with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def addKnown(self,catagory,value,fathername,fatherdbname):
        k=self.newknowns(fatherdbname)
        k.update({catagory:value})
        k["father name"]=fathername
        known_things.insert_one(k)
        ch={"change":f"added new Known {dbname} with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def getknown(self,param,val):
            k=known_things.find_one({param: val})
            return k

    def UpdateOneKnown(self,param,val,catagory,newvalue):
        k=self.getknown(param, val)
        ch={"change":f"updated a known {k['father collction']} with the catagory: {catagory} at the value: {newvalue}  for the known {k['father collction']}: ({k['name']}),old values are: ({catagory},{k[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        k.update({catagory: newvalue})
        known_things.find_one_and_replace({param: val}, k)
    
    def UpdatenewPlants(self,fathercollction,catagory,newvalue):
        newknown=self.newknowns(fathercollction)
        ch={"change":f"updated {newknown} with the catagory: {catagory} at the value: {newvalue} for : (newknown), old values are: ({catagory},{newknown[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newknown.update({catagory: newvalue})
        new.find_one_and_replace({"new": f"{newknown}"},newknown)
        
class productsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newproduct"})
        del c["_id"]
        self.newProduct=c
        
    def Add(self,catagory,value):
        prod=self.newProduct
        prod.update({catagory:addedData})
        products.insert_one(prod)
        ch={"change":f"added new product with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
        prod=products.find_one({param: val})
        return prod

    def Del(self,catagory,value):
        products.find_one_and_delete({catagory:value})
        ch={"change":f"deleted a product with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Update(self,param,val,catagory,newvalue):
        prod=self.Get(param, val)
        ch={"change":f"updated product with the catagory: {catagory} at the value: {newvalue}  for the activity: ({prod['name']}),old values are: ({catagory},{prod[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        prod.update({catagory: newvalue})
        products.find_one_and_replace({param: val}, prod)
        animals.find_one_and_replace({param: val}, animal)

    def UpdateNew(self,catagory,newvalue):
        newProduct=self.newProduct
        ch={"change":f"updated newProduct with the catagory: {catagory} at the value: {newvalue} for : (newProduct), old values are: ({catagory},{newProduct[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newProduct.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newProduct"},newProduct)

class eventsdb():
    def __init__(self):
        self.TheBest="Khalid"
        c=new.find_one({"new":"newevent"})
        del c["_id"]
        self.newEvent=c
        
    def Add(self,catagory,value):
        ev=self.newEvent
        ev.update({catagory:value})
        events.insert_one(act)
        ch={"change":f"added new activity with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Del(self,catagory,value):
        events.find_one_and_delete({catagory:value})
        ch={"change":f"deleted an event with the catagory: {catagory} at the value: {value}","time":datetime.now()}
        changes.insert_one(ch)
    
    def Get(self,param,val):
            ev=events.find_one({param: val})
            return ev

    def Update(self,param,val,catagory,newvalue):
        ev=self.Get(param, val)
        ch={"change":f"updated events with the catagory: {catagory} at the value: {newvalue}  for the event: ({ev['name']}),old values are: ({catagory},{ev[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        ev.update({catagory: newvalue})
        events.find_one_and_replace({param: val}, ev)
    
    def UpdateNew(self,catagory,newvalue):
        newEvent=self.newEvent
        ch={"change":f"updated newEvent with the catagory: {catagory} at the value: {newvalue} for : (newEvent), old values are: ({catagory},{newEvent[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        newEvent.update({catagory: newvalue})
        new.find_one_and_replace({"new": "newEvent"},newEvent)

class qdb():
    def __init__(self,):
        self.collection = mydb["questions"]

    def Add(self, question, answer, answer_from):
        question_data = {
            'question': question,
            'answer': answer,
            "who gave the answer":answer_from
        }
        Qs.insert_one(question_data)
        ch={"change":f"added the question {question} With the answer : {answer}","time":datetime.now()}
        changes.insert_one(ch)
        say('Question added successfully!')

    def Update(self, question, new_answer):
        query = {'question': question}
        answer=self.collection.find_one(query)['answer']
        new_data = {'$set': {'answer': new_answer}}
        ch={"change":f"edited the question {question} With the new answer : {new_answer}, old answer is : {answer}","time":datetime.now()}
        changes.insert_one(ch)
        self.collection.update_one(query, new_data)
        say('Question updated successfully!')

    def Del(self, question):
        query = {'question': question}
        answer=self.collection.find_one(query)['answer']
        self.collection.delete_one(query)
        ch={"change":f"deleted the question {question} With the answer : {answer}","time":datetime.now()}
        changes.insert_one(ch)
        say('Question deleted successfully!')

    def Get(self, question):
        """Get the answer to a question from the database, or search for the answer if not found."""
        query = {'question': question}
        question_data = self.collection.find_one(query)

        if question_data:
            return question_data['answer']
        else:
            pinfclss=predict_class(question,peinfwords,peinfclasses,peinfmodle)
            pinfo=get_personinfo(pinfclss,peinf)
            say(pinfclss)
            if not pinfo=="non":
                pram=get_pram(question)
                peerr=peopledb().getperson(pram[0],pram[1])
                if peerr:
                    an=peerr[pinfo]
                    say(an)
                else:
                    qq(question)
                    say('Question not found in the database.')
                    say('Searching for the answer...')
                    answer = self.googlit(question)
                    if answer[1]=='result was not found!':
                        say("what is the right answer?")
                        modee("isupq")
                    else:
                        mcount.find_one_and_replace({"no":4}, {"no":4,"a":answer})
                        say(f"is {answer[1]} the correct answer?")
                        modee("isan") 
            else:
                qq(question)
                say('Question not found in the database.')
                say('Searching for the answer...')
                answer = self.googlit(question)
                if answer[1]=='result was not found!':
                    say("what is the right answer?")
                    modee("isupq")
                else:
                    mcount.find_one_and_replace({"no":4}, {"no":4,"a":answer})
                    say(f"is {answer[1]} the correct answer?")
                    modee("isan")
  
    def googlit(self,question):
        res=[]
        po=[]
        result=None
        wikres=None
        url= f"https://www.google.com/search?q={question}"
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0"}
        page = requests.get(url,headers=headers)
        soup=BeautifulSoup(page.content,"html.parser")
        k=soup.find(class_="Z0LcW t2b5Cf")
        m=soup.find("b")
        kl=soup.find('div',{'class': "IZ6rdc"})
        g=soup.find('div',{'class': "dDoNo vrBOv vk_bk"})
        l=soup.find('h2',{'class': 'qrShPb kno-ecr-pt PZPZlf q8U8x'})
        lis=soup.find_all('div',{'class': "bVj5Zb FozYP"})
        los=soup.find_all('div',{'class': "WGwSK ghJsNe"})
        v=soup.find('div',{'class': "wwUB2c PZPZlf E75vKf"})
        
        if k:
            result=k.get_text()
        elif g:
            result=g.get_text()
        elif kl:
            result=kl.get_text()
        elif lis:
            for i in lis:
                po.append(i.get_text())
            result=None
        elif los:
            for i in los:
                po.append(i.get_text())
            result=None
        
        elif l :
            result=l.get_text()
        elif m:
            result=m.get_text()
        else:
            result=None
        if v:
            morres=v.get_text()
        res.append(question)
        first_result = soup.find("div", {"class": "yuRUbf"}).a["href"]
        

        if "wikipedia.org/wiki/"in first_result:
            result_response = requests.get(first_result)
            result_soup = BeautifulSoup(result_response.text, 'html.parser')
            y = result_soup.find('p')
            if y:
                h=y.find_next_sibling('p').b
                if h:
                    wikres = h.get_text()
                else:
                    wikres=None
            else:
                wikres=None
        else:
            wikres=None
        
        if result:
            if "when" in question and "founded"in question:
                res.append(result.split(".")[0].split(",")[0]+result.split(".")[0].split(",")[1])
            else:
                res.append(sent_tokenize(result)[0])
        elif po:
            res.append(po)
        elif wikres:
            res.append(wikres)
        else:
            res.append("result was not found!")
        res.append(first_result)
        #res=['question','answer','herf']
        return res

    def close_connection(self,):
        """Close the MongoDB connection."""
        client.close()

class relationshipdb():
    def __init__(self):
        self.TheBest="Khalid"
        
    def newrelation(self,relationship):
        newr=new.find_one({"relationship":relationship})
        if newr:
            '''in["ownership","ownerships"]:
            newr=new.find_one({"new":"newonership"})
        elif relationship in["siblings","sibling","brothers","sisters","brother","sister"]:
            newr=new.find_one({"new":"newsibling"})
        elif relationship in["roommate","roommates","room mates" "room mate"]:
            newr=new.find_one({"new":"newroommate"})
        elif relationship in["teammate","teammates","team mates","team mate"]:
            newr=new.find_one({"new":"newteammate"})
        elif relationship in["class mates","classmates","classmate","class mate"]:
            newr=new.find_one({"new":"newclassmate"})
        elif relationship in["neighbor","neighbors"]:
            newr=new.find_one({"new":"newneighbor"})
        elif relationship in["parent_son","parent-son","parent son","parent","son"]:
            newr=new.find_one({"new":"newparentson"})'''
            pass
        else:
            newr={
                "new": f"new{relationship}",
                "relationship": relationship,
                "names": [],
                "ids": [],
                "date the relationship started": "0010-01-01T01:01:01",
                "date the relationship ended": "0010-01-01T01:01:01",
                "relationship discripion": "",
                "other info": []
            }
        if "_id"in newr.keys():
            del newr["_id"]
        else: 
            pass
        return newr
    
    def addperntson(self,parentname,parentid,sonname,sonid):
        newr=self.newrelation("parent_son")
        newr.update({"parent name":parentname,"son name":sonname,"parent id":parentid,"son id":sonid})
        relationships.insert_one(newr)
        ch={"change":f"added a new parent-son relationship with the parent name: {parentname} and the son name:{sonname}","time":datetime.now()}
        changes.insert_one(ch)
    
    def addownership(self,ownertname,ownertid,ownedname,ownedid,ownedtype,ownertype):
        newr=self.newrelation("ownership")
        newr.update({"owner name":ownertname,"owned name":ownedname,"owner id":ownertid,"owned id":ownedid,"owned collction name":ownedtype,"owner collction name":ownertype})
        relationships.insert_one(newr)
        ch={"change":f"added a new ownership relationship with the owner name: {ownertname} and the owned name:{ownedname}","time":datetime.now()}
        changes.insert_one(ch)
    
    def addRelationship(self,relationship,firstPname,secondPname,firstid,secondid):
        newr=self.newrelation(relationship)
        for j in [parentname,sonname]:
            newr["names"].append(j)
        for l in [parentid,sonid]:
            newr["ids"].append(l)
        relationships.insert_one(newr)
        ch={"change":f"added a new {relationship} relationship with the name: {firstPname} and the name:{secondPname}","time":datetime.now()}
        changes.insert_one(ch)
        
    def delrelationship(self,relationship,firstid,secondid):
        if relationship in["ownership","ownerships"]:
            relationships.find_one_and_delete({"owner id": firstid,"owend id":secondid})
        elif relationship in["parent_son","parent-son","parent son","parent","son"]:
            relationships.find_one_and_delete({"parent id": firstid,"son id":secondid})
        else:
            relationships.find_one_and_delete({"ids": {'$in':[firstid,secondid]}})
        ch={"change":f"deleted a {relationship} relationship between the person id: {firstid} and the person id: {secondid}","time":datetime.now()}
        changes.insert_one(ch)
    
    def getrelationship(self,firstid,seconedid):
            if relationship in["ownership","ownerships"]:
                re=relationships.find_one({"owner id": firstid,"owend id":secondid})
            elif relationship in["parent_son","parent-son","parent son","parent","son"]:
                re=relationships.find_one({"parent id": firstid,"son id":secondid})
            else:
                re=relationships.find_one({"ids": {'$in':[firstid,secondid]}})    
            return re

    def UpdateOnerelationship(self,firstid,seconedid,catagory,newvalue):
        re=self.getrelationship(firstid, seconedid)
        relationship=re["relationship"]
        ch={"change":f"updated a {relationship} relationship with the catagory: {catagory} at the value: {newvalue} for the relationship: (id :{firstid}, id:{seconedid}),old values are: ({catagory},{re[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        re.update({catagory: newvalue})
        if relationship in["ownership","ownerships"]:
            relationships.find_one_and_replace({"owner id": firstid,"owend id":secondid}, re)
        elif relationship in["parent_son","parent-son","parent son","parent","son"]:
            relationships.find_one_and_replace({"parent id": firstid,"son id":secondid}, re)
        else:
            relationships.find_one_and_replace({"ids": {'$in':[firstid,secondid]}}, re)
                
    def UpdatenewRelationship(self,relationship,catagory,newvalue):
        re=self.newrelation(relationship)
        newre=re["new"] 
        ch={"change":f"updated {newre} with the catagory: {catagory} at the value: {newvalue} for : ({newre}), old values are: ({catagory},{re[catagory]})","time":datetime.now()}
        changes.insert_one(ch)
        re.update({catagory: newvalue})
        if new.find_one({"new": newre}):
            new.find_one_and_replace({"new": newre},re) 
        else:
            new.insert_one(re)   
        
    def addperson(self,relationship,pname,pid,seconedid):
        re=relationships.find_one({"relationship":relationship,"ids":{"$in":seconedid}})
        re["ids"].append(pid)
        re["names"].append(pname)
        relationships.find_one_and_replace({"relationship":relationship,"ids":{"$in":seconedid}}, re)
        ch={"change":f"added a new person to the {relationship} relationship with the id: {seconedid} and the id:{pid}","time":datetime.now()}
        changes.insert_one(ch)
  
class diarydb():
    def __init__(self):
        self.KHALID="The Best"

    def generate_diary_title(self,entry):
        # Remove stopwords and tokenize the entry
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(entry.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]

        # Calculate word frequencies
        fdist = FreqDist(words)

        # Get the most common words
        most_common = fdist.most_common(5)  # You can adjust the number of words to consider

        # Create the title from the most common words
        title = ' '.join([word.capitalize() for word, _ in most_common])

        return title

    def add_diary_entry(self,entry,title=None):
        if not title:
            title=self.generate_diary_title(entry)
        entrys={"title":title,"entry":entry,"date":datetime.now().isoformat().replace("T", " ")}
        dairy.insert_one(entrys)

    def diary_entries(self,date):
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())

        query = {
            'date': {
                '$gte': start_of_day.isoformat().replace("T", " "),
                '$lte': end_of_day.isoformat().replace("T", " ")
            }
        }
        entries = dairy.find(query)
        return entries

    def get_diary_entries(self,date):
        entries=self.diary_entries(date)
        if entries:
            # Print the retrieved entries
            res=f"Diary entries for {date}:"
            for entry in entries:
                res+=f"\nTitle: {entry['title']}\nContent: {entry['entry']}\nDate: {entry['date']}"
        else:
            res=f"no entries found for {date}"
        return res


user_loc=peopledb().getperson("name", "khalid afif sami iqnaibi")["location"]
# Initialize the TTS engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)
engine.setProperty('rate', 225)  # Speed of speech
  

lemmatizer = WordNetLemmatizer()
# loading the files we made previously
with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/emo.json','r') )as f:
    emos=json.load(f)
emowords = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/emowords.pkl', 'rb'))
emoclasses = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/emoclasses.pkl', 'rb'))
emomodel = load_model('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/chatbotemo.h5')

with (open("C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/intents.json",'r') )as f:
    ints=json.load(f)
    
with (open("C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/command.json",'r') )as f:
    cmnds=json.load(f)
cmndwords =  pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/cmndwords.pkl', 'rb'))
cmndclasses = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/cmndclasses.pkl', 'rb'))
cmndmodle = load_model('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/chatbotcmnd.h5')

with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/comm.json','r') )as f:
    comms=json.load(f)
commwords =  pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/commwords.pkl', 'rb'))
commclasses = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/commclasses.pkl', 'rb'))
commmodle = load_model('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/chatbotcomms.h5')

with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/perdb.json','r') )as f:
    peinf=json.load(f)
peinfwords =  pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/peinfwords.pkl', 'rb'))
peinfclasses = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/peinfclasses.pkl', 'rb'))
peinfmodle = load_model('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/chatbotpeinf.h5')

with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/actvdb.json','r') )as f:
    actv=json.load(f)
actvwords =  pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/actvwords.pkl', 'rb'))
actvclasses = pickle.load(open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/actvclasses.pkl', 'rb'))
actvmodle = load_model('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/chatbotactv.h5')

lrn=''
nlp = spacy.load('en_core_web_md')
propapilty=float (0.001)
emotion='nutral'
ha=100
sa=0
an=0
sc=0
dis=0
tird=0
awk=0
brd=0
emb=0
grt=15


class Sen():
    def __init__(self):#,sentence):
        self.khalid='The best'
        self.potato='YES'
        #self.Subject=self.get_subject(sentence)
        #self.Object=self.get_object(sentence)
        #self.Place=self.get_place(sentence)
        #self.Time=self.get_time(sentence)
    def get_subject(self,sentence):
        doc = nlp(sentence)
        for token in doc:
            if ("subj" in token.dep_):
                subtree = list(token.subtree)
                start = subtree[0].i
                end = subtree[-1].i + 1
                return doc[start:end]
    def get_object(self,sentence):
        doc = nlp(sentence)
        for token in doc:
            if ("dobj" in token.dep_):
                subtree = list(token.subtree)
                start = subtree[0].i
                end = subtree[-1].i + 1
                return doc[start:end]
    def get_time(self,sentence):
        time={'time':[],'date':[],'day':[]}
        def time_diffr(sentence):
            doc = nlp(sentence)
            m={'time':[],'date':[],'day':[]}
            tims=['all',]
            day=['today','Today','Yesterday','yesterday'
                 ,'monday','Monday','sunday','Sunday',
                 'tuesday','Tuesday','Friday','Friday','Saturday',
                 'saturday','thursday','Thursday','wednesday',
                 'Wednesday']
            for ent in doc.ents:
                k=False
                # Check if the entity is a time, day, or date
                if ent.label_ == "TIME":
                    m['time'].append(ent.text)
                elif ent.label_ == "DATE":
                    for i in day :
                        if i in ent.text:
                            k=True
                            m['day'].append(ent.text)
                    for i in tims:
                        if i in ent.text:
                            k=True
                            m['time'].append(ent.text)
                    if not k:
                        m['date'].append(ent.text)
                elif ent.label_ == "DAY":
                    m['day'].append(ent.text)
                else:
                    pass
            return m
        def get_tim(sentence):
            s=[]
            timeph=['tonight','the evening',"evening",
                    'when i was at school','this week',
                    'next week']
            popo=True
            for i in timeph:
                if i in sentence:
                    for j in s:
                        if ( i in j):
                            popo=False
                    if popo:
                        s.append(i)
                else:
                    pass
            return s
        potato=time_diffr(sentence)
        tm= get_tim(sentence)
        if potato:
            for i in potato['time']:
                time['time'].append(i)
            for j in potato['day']:
                time['day'].append(j)
            for c in potato['date']:
                time['date'].append(c) 
        for k in tm:
            time['time'].append(k)
        return time
    def get_place(self,sentence):
        s=[]
        # Tokenize the sentence into words
        words = word_tokenize(sentence)
        doc=nlp(sentence)
        def pos_tag(wrd) :
            k=[]
            c=0
            dc = doc
            for i in dc:
                if c == wrd:
                    k.append([i.text,i.pos_])
                c=c+1
            return k
        for wrd in range(len(words)):
            if (pos_tag(wrd)[0][1] == "ADP"and words[wrd]not in ['for','with','by','of']or (wrd+1<len(words)and words[wrd] in ['by']and words[wrd+1] in ['the'])):
                plc=''
                if ((wrd+1)<len (words)):
                    i=wrd+1
                    while (pos_tag(i)[0][1] in ["DET","ADJ","PRON","CCONJ",'PROPN',"ADP","NOUN"]and (words[i]not in ['for','with','last','of','by','evenings','evening']or (words[i] in ['by']and words[i+1] in ['the']))):
                        if (pos_tag(i)[0][1]in["DET","ADJ","PRON","CCONJ","ADP"])and((i+1)<len (words))and(pos_tag(i+1)[0][1] not in ["DET",'PROPN',"PRON","ADJ","CCONJ","PRP$","NOUN"]or words[i+1] in ['for','with','last','of','by','evenings','evening']):
                            break
                        elif (pos_tag(i)[0][1]in["DET","ADJ","PRON","CCONJ","ADP"])and((i+1)==len (words)):
                            break
                        else:
                            plc = plc + words[i]+" "
                        if ((i+1)<len (words)):
                            i=i+1
                        else:
                            break
                    if (plc == ''):    
                        pass
                    else:
                        if ((len(s)>0)and(plc in s[-1])):
                            pass
                        else:
                            s.append(plc)
                else:
                    pass
            elif ((wrd>0)and (wrd+1)<len (words)and pos_tag(wrd)[0][1] == 'VERB'and pos_tag(wrd+1)[0][1]in["ADJ","PRON","DET"]and words[wrd+1]not in ['a','an']and pos_tag(wrd-1)[0][1]not in ['PART'])or (words[wrd] in ['visited']):
                plc=''
                if ((wrd+1)<len (words)):
                    i=wrd+1
                    while (pos_tag(i)[0][1] in ["DET","ADJ","PRON",'PROPN',"CCONJ","ADP","NOUN"]and (words[i]not in ['for','with','last','of','by','evenings','evening']or (words[i] in ['by']and words[i+1] in ['the']))):
                        if (pos_tag(i)[0][1]in["DET","ADJ","PRON","CCONJ","ADP"])and((i+1)<len (words))and(pos_tag(i+1)[0][1] not in ["DET",'PROPN',"PRON","ADJ","CCONJ","PRP$","NOUN"]or words[i] in ['for','with','last','of','by','evenings','evening'] ):
                            break
                        elif (pos_tag(i)[0][1]in["DET","ADJ","PRON","CCONJ","ADP"])and(i+1)==len (words):
                            break
                        else:
                            plc = plc + words[i]+" "
                        if ((i+1)<len (words)):
                            i=i+1
                        else:
                            break
                    if (plc == ''):    
                        pass
                    else:
                        if ((len(s)>0)and(plc in s[-1])):
                            pass
                        else:
                            s.append(plc)
                else:
                    pass
        return s
     
class Ktime():
    def __init__(self):
        self.KHALID="The Best"
    
    def txttoint(self,text):
        """
        Converts number words in text to integers.
        """
        NUMBERS = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
            'sixty': 60,
            'seventy': 70,
            'eighty': 80,
            'ninety': 90,
            'hundred': 100,
            'thousand': 1000,
            'million': 1000000,
            'billion': 1000000000,
            'trillion': 1000000000000
        }
        doc = nlp(text)
        nums = []
        nno=0
        for token in doc:
            if token.text.isdigit() or token.text.lower() in NUMBERS:
                nums.append([token.text,doc[nno+1].text])
            else:
                pass
            nno=nno+1
        re=[]
        for i in nums:
            re.append(i[0])
            if not(i[1].isdigit() or i[1] in NUMBERS or i[1] in ['and','-','.']):
                xx=i[1]
                re.append(i[1])
        if (len(re)>0) and(type(re[-1])==int or re[-1].isdigit() or re[-1] in NUMBERS) :
            re.append(xx)
        mm=[]
        mc=[]
        g=1
        gc=0
        result=[]
        cout=-1
        isv=""
        for kl in re:
            cout=cout+1
            if type(kl)==int or kl.isdigit():
                mm.append(int(kl))
            elif kl in NUMBERS and kl not in ['zero','one','two','three','four','five','six','seven','eight', 'nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']:
                mm.append(NUMBERS[kl])
                for k in mm:
                    g=g*k
                mm=[]
                mc.append(g)
                g=1
            elif kl in ['one','two', 'three','four','five','six','seven','eight', 'nine']:
                if (re[cout+1].isdigit())or (re[cout+1] in NUMBERS )or (type(re[cout+1]) == int )or not(cout==len(re)-1):
                    mm.append(NUMBERS[kl])
                else:
                    mc.append(NUMBERS[kl])
            elif kl in ['twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']:
                mc.append(NUMBERS[kl])
            elif kl in ['zero','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']:
                mm.append(NUMBERS[kl])
                for k in mm:
                    g=g*k
                mm=[]
                mc.append(g)
                g=1
            elif type(kl)==str and cout==len(re)-1:
                isv=kl
            else:
                if mm==[]:
                    pass
                else:
                    for k in mm:
                        g=g*k
                    mm=[]
                    mc.append(g)
                    g=1
                if mc==[]:
                    pass
                else:
                    for l in mc:
                        gc=gc+l
                    result.append(gc)
                    gc=0
                    result.append(kl)
                    mm=[]
                    mc=[]
        if mm==[]:
            pass
        else:
            for k in mm:
                g=g*k
            mm=[]
            mc.append(g)
            g=1
        if mc==[]:
            pass
        else:
            for l in mc:
                gc=gc+l
            result.append(gc)
            mm=[]
            mc=[]
        if not isv == '':
            result.append(isv) 
        return result

    def relative_time(self,time_description,isodate):
        days=0
        mons=0
        wrds=word_tokenize(time_description)
        years=0
        secs=0
        op="pl"

        for wrd in wrds:
            if wrd in ["before","ago"]:
                op="mi"
            elif wrd in ["after"]:
                op="pl"
            else:
                pass

        date=datetime.fromisoformat(isodate)
        re=self.txttoint(time_description)
        for i in range(len(re)):
            if i+1<len(re) and type(re[i])==int:
                if re[i+1] in ["day","days"]:
                    days=re[i]*1
                elif re[i+1] in ["week","weeks"]:
                    days=re[i]*7
                elif re[i+1]in ["months","month"]:
                    mons=re[i]*1
                elif re[i+1] in ["year","years"]:
                    years=re[i]*1
                elif re[i+1] in ["decade","decades"]:
                    years=re[i]*10
                elif re[i+1] in ["century","centurys"]:
                    years=re[i]*100
                elif re[i+1] in ["hour","hours"] :
                    secs=re[i]*3600
                elif re[i+1] in ["minutes","minute"]:
                    secs=re[i]*60
                elif re[i+1]in ["second","seconds"]:
                    secs=re[i]*1
                else:
                    pass
            else:
                pass
        if len(re)<1:
            if "day"in time_description or "days"in time_description :
                days=1
            elif "week"in time_description or "weeks"in time_description:
                days=7
            elif "months"in time_description or "month"in time_description:
                mons=1
            elif "year"in time_description or "years"in time_description:
                years=1
            elif "decade"in time_description or "decades"in time_description:
                years=10
            elif "century"in time_description or "centurys"in time_description:
                years=100
            elif "hour"in time_description or "hours"in time_description:
                secs=3600
            elif "minutes"in time_description or "minute"in time_description:
                secs=60
            elif "second"in time_description or "seconds"in time_description:
                secs=1
            else:
                pass
        else:
            pass
        kha=True
        while kha:
            if (date.month in [0,1,3,5,7,8,10,12]) and (days>30):
                mons=mons+1
                days=days-31
            elif (date.month in [4,6,9,11]) and (days>29):
                mons=mons+1
                days=days-30
            elif (date.month ==2 and days>28) and (date.year%4==0):
                mons=mons+1
                days=days-29
            elif (date.month ==2 and days>27) and not (date.year%4==0):
                mons=mons+1
                days=days-28
            else:
                kha=False

        while mons>11:
            years=years+1
            mons=mons-12

        while secs>86399:
            days=days+1
            secs=secs-86400
            
        if op=="pl":
            result=date
            if date.second+ secs>86399:
                days=days+1
                secs=secs-86400
                result=result.replace(second=secs)
            else:
                result=result.replace(second=date.second+secs)
            
            if date.month in [1,3,5,7,8,10,12] and date.day+days>30:
                mons=mons+1
                days=(date.day+days)-31
                result=result.replace(day=days)
            elif date.month in [4,6,9,11] and date.day+days>29:
                mons=mons+1
                days=(date.day+days)-30
                result=result.replace(day=days)
            elif date.month in [2] and date.day+days>28 and date.year%4==0:
                mons=mons+1
                days=(date.day+days)-29
                result=result.replace(day=days)
            elif date.month in [2] and date.day+days>27 and not date.year%4==0:
                mons=mons+1
                days=(date.day+days)-28
                result=result.replace(day=days)
            else:
                result=result.replace(day=date.day+days)
                
            if (date.month+ mons)>11: 
                years=years+1
                mons=(date.month+ mons)-12
                result= result.replace(month = mons)
            elif mons>0:
                if date.month + mons == 2 and result.day==29 and not date.year + years%4==0:
                    result= result.replace( month = 3, day = 1)
                else:
                    result= result.replace(month = (date.month + mons))
            else:
                pass        
            
            if years>0:
                if result.month == 2 and result.day==29 and not date.year + years%4==0 :
                    result= result.replace(year = (date.year + years), month = 3, day = 1)
                else:
                    result= result.replace(year = (date.year + years))              
        elif op == "mi":
            result=date
            if date.second- secs<0:
                days=days+1
                secs=86400+(date.second-secs)
                result=result.replace(second=secs) 
            else:
                result=result.replace(second=date.second-secs) 
                
            if date.month in [1,3,5,7,8,10,12] and date.day-days<0:
                mons=mons+1
                days=31+(date.day-days)
                result=result.replace(day=days)
            elif date.month in [4,6,9,11] and date.day-days<0:
                mons=mons+1
                days=30+(date.day-days)
                result=result.replace(day=days)
            elif date.month in [2] and date.day-days<0 and date.year%4==0:
                mons=mons+1
                days=29+(date.day-days)
                result=result.replace(day=days)
            elif date.month in [2] and date.day-days<0 and not date.year%4==0:
                mons=mons+1
                days=28+(date.day-days)
                result=result.replace(day=days)
            else:
                result=result.replace(day=date.day-days)
            if date.month- mons<0: 
                years=years+1
                mons=12+(date.month- mons)
                result= result.replace(month = mons)
            elif mons>0:
                if date.month - mons == 2 and result.day==29 and not date.year - years%4==0:
                    result= result.replace( month = 2, day = 28)
                else:
                    result= result.replace(month = (date.month - mons))
            if years>0:
                if result.month== 2 and result.day==29 and not date.year - years%4==0:
                    result= result.replace(year = (date.year - years), month = 2, day = 28)
                else:
                    result= result.replace(year = (date.year - years))
            else:
                pass       
            
                

        else:
            result=date
        return result

    def extract_date(self,txt):
        wrds=word_tokenize(txt)
        da=[]
        for i in range(len(wrds)):
            if not wrds[i] in ['and',"also"]:
                try:
                    date = parse(wrds[i], fuzzy=True)
                    t=datetime.now().time()
                    if i+1<len(wrds)and wrds[i+1]in["am","pm"] or i-1>0 and wrds[i-1]in["at"] :
                        if wrds[i+1] == 'pm':
                            t=date+timedelta(hours=12)
                            t=t.time()
                        else:
                            t=date.time()
                    else:
                        d=date.date()
                except ValueError:
                        pass
            else:
                da.append({"date":d,"time":t})
        da.append({"date":d,"time":t})

        dates=[]

        for dd in da:
            dates.append(datetime.combine(dd["date"],dd["time"]))

        return dates

    def get_whenwas(self,text):
        dates=self.extract_date(text)
        if len(dates)>1: 
            whenwas=[]
            for j in dates:
                res=self.when_was(j)
                k=True
                if res["time"]=="future":
                    whnwas=f'{j} is after'
                elif res['time']=='past':
                    whnwas=f'{j} was'
                elif res["time"]=="now":
                    whnwas=f"{j} is now"
                    whenwas.append({i:whnwas})
                    break
                else:
                    whnwas="4OO0OO4 :("
                    whenwas.append({i:whnwas})
                    break
                for i in res:
                    if not i in["time"]and not res[i]==0 and k:
                        whnwas=whnwas+" "+str(abs(res[i]))+" "+i
                        k=False
                    elif not i in["time"]and not res[i]==0:
                        whnwas=whnwas+" and "+str(abs(res[i]))+" "+i
                    elif res[i]in['past']:
                        whnwas=whnwas+" ago"
                    else:
                        pass
                whenwas.append({i:whnwas})
        elif len(dates)==1:
            res=self.when_was(dates[0])
            k=True
            if res["time"]=="future":
                whenwas=f'{dates[0]} is after'
            elif res['time']=='past':
                whenwas=f'{dates[0]} was'
            elif res["time"]=="now":
                return f"{dates[0]} is now"
            else:
                return "4OO0OO4 :("
            for i in res:
                if not i in["time"]and not res[i]==0 and k:
                    whenwas=whenwas+" "+str(abs(res[i]))+" "+i
                    k=False
                elif not i in["time"]and not res[i]==0:
                    whenwas=whenwas+" and "+str(abs(res[i]))+" "+i
                elif res[i]in['past']:
                    whenwas=whenwas+" ago"
                else:
                    pass
        else:
            whenwas="invalid input.."
        
        return whenwas

    def when_was(self,date):
        result={"years":date.year-datetime.now().year,"monthes":date.month-datetime.now().month,"days":date.day-datetime.now().day,"hours":date.hour-datetime.now().hour,"minutes":date.minute-datetime.now().minute,"seconds":date.second-datetime.now().second,"time":""}
        ww=date-datetime.now()
        if ww.total_seconds() > 0:
            result["time"]="future"
        elif ww.total_seconds() < 0:
            result["time"]="past"
        else:
            result["time"]="now"
        return result

    def get_relative_time(self,time_description,isodate):
        if time_description == "tommorow":
            result= datetime.fromisoformat(isodate)+timedelta(days= datetime.fromisoformat(isodate).day+1)
        elif time_description == "today":
            result= datetime.fromisoformat(isodate)
        elif time_description == "yesterday":
            result= datetime.fromisoformat(isodate)+timedelta(days= datetime.fromisoformat(isodate).day-1)
        else:
            tim=Sen().get_time(time_description)
    
            td=""
            for i in tim:
                for l in tim[i]:
                    td=td+l+" and "
    
            result=self.relative_time(td,isodate) 
        return result

class kweather():
    def __init__(self):
        self.KHALID="the best"
        self.apikey=W_API_KEY

    def add_days(self,location=user_loc):
        api_key = self.apikey  # Replace with your WeatherAPI.com API key
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        # Make a request to the WeatherAPI.com API
        response = requests.get(base_url, params={"key": api_key, "q": location, "days": 3, "aqi": "no", "alerts": "no"})
        data = response.json()
        hourly_forecasts = data["forecast"]["forecastday"]
        for i in hourly_forecasts:
            for j in i["hour"]:
                j.update({"location":data["location"]["name"].lower()+" "+data["location"]["country"].lower()})
                weather.insert_one(j)
    
    def accurate_weather(self,location=user_loc):
        api_key = self.apikey # Replace with your WeatherAPI.com API key
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        # Make a request to the WeatherAPI.com API
        response = requests.get(base_url, params={"key": api_key, "q": location, "days": 3, "aqi": "no", "alerts": "no"})
        data = response.json()
        return data["current"]
    
    def get_accurate_weather(self,location=user_loc):
        data=self.accurate_weather(location=location)
        
        # Extract relevant information from the response
        if "error" in data:
            result="An error occurred:"+data["error"]["message"]
        else:
            current_temp = data["temp_c"]
            feels_like_temp = data["feelslike_c"]
            condition = data["condition"]["text"]
            wind_speed = data["wind_kph"]
            humidity = data["humidity"]
            visibility = data["vis_km"]
            pressure = data["pressure_mb"]
            result=f"Weather update for {location}:\nTemperature: {current_temp}°C\nFeels Like: {feels_like_temp}°C\nCondition: {condition}\nWind Speed: {wind_speed} kph\nHumidity: {humidity}%\nVisibility: {visibility} km\nPressure: {pressure} mb"
    
        return result    
    
    def add_forcast(self,location=user_loc):
        api_key = self.apikey  # Replace with your WeatherAPI.com API key
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        # Make a request to the WeatherAPI.com API
        response = requests.get(base_url, params={"key": api_key, "q": location, "days": 3, "aqi": "no", "alerts": "no"})
        data = response.json()
        hourly_forecasts = data["forecast"]["forecastday"]
        for i in hourly_forecasts:
            print(i)
            j = i["day"]
            j.update({"time":i["date"],"location":data["location"]["name"].lower()+" "+data["location"]["country"].lower()})
            forecast.insert_one(j)    
        
    def get_weather(self,location,time):
        res=weather.find_one({"location":location,"time":time.isoformat().replace("T", " ")[:-3]})
        return res    
        
    def weather_now(self,location=user_loc):
        res=self.get_weather(location, datetime.now()-timedelta(minutes=datetime.now().time().minute,seconds=datetime.now().time().second,microseconds=datetime.now().time().microsecond))
        return res

    def get_weather_update(self,location=user_loc,time=datetime.now()):
        time=time-timedelta(minutes=time.time().minute,seconds=time.time().second,microseconds=time.now().time().microsecond)
        data=self.get_weather(location=location,time= time)
        if not data:
            self.add_days(location=location)
            data=self.get_weather(location= location,time= time)
        
        # Extract relevant information from the response
        if "error" in data:
            result="An error occurred:"+data["error"]["message"]
        else:
            ocation = data["location"]
            current_temp = data["temp_c"]
            feels_like_temp = data["feelslike_c"]
            condition = data["condition"]["text"]
            wind_speed = data["wind_kph"]
            humidity = data["humidity"]
            visibility = data["vis_km"]
            pressure = data["pressure_mb"]
            cor= data["chance_of_rain"]
            # Print the current weather update
            result=f"Weather update for {location}:\nTemperature: {current_temp}°C\nFeels Like: {feels_like_temp}°C\nCondition: {condition}\nWind Speed: {wind_speed} kph\nHumidity: {humidity}%\nVisibility: {visibility} km\nPressure: {pressure} mb\nChance of Rain: {cor}%"
    
        return result

    def get_forcast(self,location=user_loc,date=datetime.now().date()):
        daily_forecasts = self.forcast(location=location,date=date) 
        result="Daily Forecasts:"
        # Print daily forecasts for the upcoming days
        for forecast in daily_forecasts:
            date = forecast["time"]
            min_temp = forecast["mintemp_c"]
            max_temp = forecast["maxtemp_c"]
            condition = forecast["condition"]["text"]
            chance_of_rain = forecast["daily_chance_of_rain"]
            result+=f"\nDate: {date}, Min Temperature: {min_temp}°C, Max Temperature: {max_temp}°C, Condition: {condition}, Chance of Rain: {chance_of_rain}%"
        return result
    
    def forcast(self,location=user_loc,date=datetime.now().date()):
        data = forecast.find_one({"time":date.isoformat(),"location":location})
        if not data:
            self.add_forcast(location=location)
            data=forecast.find_one({"time":date.isoformat(),"location":location})
        forecasts=[]
        for i in range(3):
            forecasts.append(forecast.find_one({"time":date.isoformat(),"location":location}))
            date=date+timedelta(days=1)
        return forecasts

    def get_hourly_forcast(self,location=user_loc,time=datetime.now()):
        hourly_forecasts=self.hourly_forcast(location=location,time=time)
        result="Hourly Forecasts:"
        # Print hourly forecasts for the day
        for forecast in hourly_forecasts:
            time = forecast["time"]
            temperature = forecast["temp_c"]
            feels_like_temp = forecast["feelslike_c"]
            condition = forecast["condition"]["text"]
            result+=f"\nTime: {time}, Temperature: {temperature}°C, Feels Like: {feels_like_temp}°C, Condition: {condition}"

        return result

    def hourly_forcast(self,location=user_loc,time=datetime.now()):
        time=time-timedelta(hours=time.time().hour, minutes=time.time().minute,seconds=time.time().second,microseconds=time.now().time().microsecond)
        data=self.get_weather(location, time)
        if not data:
            self.add_days(location=location)
            data=self.get_weather(location, time)
        
        # Extract relevant information from the response
        if "error" in data:
            result="An error occurred:"+data["error"]["message"]
        else:
            hourly_forecasts=[]
            for i in range(24):
                time=time+timedelta(hours=1)
                hourly_forecasts.append(self.get_weather(location, time))
        return hourly_forecasts
    
def feels(happy,sad,angry,sceared,discusted,tiredness,awkwardness,boredom,embressed,greatful):
    ha=ha+happy
    sa=sa+sad
    an=an+angry
    sc=sc+sceared
    dis+dis+discusted
    tird=tird+tiredness
    awk=awk+awkwardness
    brd=brd+boredom
    emb=emb+embressed
    grt=grt+greatful
    print(ha,sa,an,sc,dis,tird,awk,brd,emb,grt)    
         
def clean_up_sentences(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) 
                      for word in sentence_words]
    return sentence_words
# Preprocess the text data
def preprocess(text):
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Convert to lowercase
    text = text.lower()
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stop words
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return tokens
# Extract the features from the text data
def extract_features(text,fdist):
    words = set(text)
    features = {}
    for word in fdist.keys():
        features[word] = (word in words)
    return features

def extract_qustion(text):
    
    l=[]
    # Load the large English NLP model
    nlp = spacy.load("en_core_web_sm")

    # Create a doc object and apply NLP on the text
    doc = nlp(text)

    def split_sentences_with_ai(text):
        # Using the sent_tokenize function from the nltk library
        sentences = sent_tokenize(text)
    
        # Return the list of sentences
        return sentences
    
    questions = comms['intents'][2]['patterns']
    conversations = ["Hi, how are you?", 
                 'my frind is cold',
                 'i like potato',
                 'i went to school two days ago',
                 "Nice day today, isn't it?",
                 "I like to play basketball on weekends."]

    # Convert the data into numerical representation
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(questions + conversations)
    y = np.array([0] * len(questions) + [1] * len(conversations))

    # Train the Naive Bayes classifier
    clf = MultinomialNB().fit(X, y)

    # Test the classifier with new sentences
    new_sentences = split_sentences_with_ai(text)
    X_test = vectorizer.transform(new_sentences)
    predictions = clf.predict(X_test)

    # Print the results
    for i, prediction in enumerate(predictions):
        if prediction == 0:
            l.append(new_sentences[i])
    return l

def txtcllassfie(txxt,json):
    # Define the categories of text inputs
    categories = ['story', 'command', 'qustion', 'conversation', 'facts']
    # Define the training data
    comm=json
    
    training_data=[]
    for i in comm['intents']:
        clas=i['tag']
        for j in i['patterns']:
            txt=j 
            training_data.append((txt,clas))
    # Preprocess the training data and create a list of tuples containing the text and category
    processed_data = [(preprocess(text), category) for text, category in training_data]

    
    # Create a frequency distribution of the words in the training data
    all_words = []
    for words, category in processed_data:
        all_words.extend(words)
    fdist = FreqDist(all_words)
    
    # Create a list of feature sets
    feature_sets = [(extract_features(text,fdist), category) for (text, category) in processed_data]  
      
    # Train the Naive Bayes classifier on the feature sets
    classifier = NaiveBayesClassifier.train(feature_sets)
    
    # Test the AI on a new text input
    processed_text = preprocess(txxt)
    features = extract_features(processed_text,fdist)
    return classifier.classify(features)

def autolrn(sen,tag,lrn):
    addt=input('is the prdiction true and cant have any other tag in other contics\n>> ')
    if addt=='yes'or addt=='yup'or addt=='true'or addt=='TRUE'or addt=='True':
        addto=True
    else:
        addto=False
    if addto:
        for i in intents['intents']:
            if tag ==i['tag']:
                if sen in i['patterns']:
                    pass
                else:
                    i['patterns'].append(sen)
            else :
                pass
        if lrn=='emo':
            with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/emo.json','w')) as file:
                    json.dump(intents,file,indent=6)
        if lrn=='int':
            with (open('C:/Users/khaaf/Desktop/code/A.S.H/pyapp/ash_ai/emo.json','w')) as file:
                    json.dump(intents,file,indent=6)
            
    else:
        say('tell me when to add stuf so i can learn them :)')

def bagw(sentence,wrdspkl):
    # separate out words from the input sentence
    sentence_words = clean_up_sentences(sentence)
    bag = [0]*len(wrdspkl)
    for w in sentence_words:
        for i, word in enumerate(wrdspkl):
            # check whether the word
            # is present in the input as well
            if word == w:
                # as the list of words
                # created earlier.
                bag[i] = 1
    # return a numpy array
    return np.array(bag)

def predict_class(sentence,wordspkl,classespkl,model):
    bow = bagw(sentence,wordspkl)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.3
    results = [[i, r] for i, r in enumerate(res) 
               if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classespkl[r[0]],
                            'probability': str(r[1])})
        return return_list

def get_emo(emo_list,emo_json):
    probability=float(emo_list[0]['probability'])
    tag = emo_list[0]['intent']
    list_of_emos=emo_json['intents']
    emogot =''
    for i in list_of_emos:
        if i['tag']==tag:
            emogot=tag
            break
    if (probability<.85):
        emogot='nutral'
    return(emogot)

def get_type(comm_list,comm_json):
    tag = comm_list[0]['intent']
    list_of_comms=comm_json['intents']
    typegot =''
    for i in list_of_comms:
        if i['tag']==tag:
            typegot=tag
            break
    #print(comm_list)
    return(typegot)
    
def get_command(cmnd_list,cmnd_json):
    tag = cmnd_list[0]['command']
    list_of_cmnds=cmnd_json['command']
    cmndgot =''
    for i in list_of_cmnds:
        if i['tag']==tag:
            cmndgot=tag
            break
    return(cmndgot)    

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    result = ""
    for i in list_of_intents:
        if i['tag'] == tag:
            
              # prints a random response
            random.choice(i['responses'])  
            break
    #autolrn(message,tag,'int')
    return(result)

def get_personinfo(peinf_list,peinf_json):
    probability=float(peinf_list[0]['probability'])
    tag = peinf_list[0]['intent']
    list_of_peinf=peinf_json['intents']
    peinfgot =''
    for i in list_of_peinf:
        if i['tag']==tag:
            peinfgot=tag
            break
    if (probability<.88):
        peinfgot='non'
    return(peinfgot)  

def get_actvinfo(actv_list,actv_json):
    probability=float(actv_list[0]['probability'])
    tag = actv_list[0]['intent']
    list_of_actv=actv_json['intents']
    actvgot =''
    for i in list_of_actv:
        if i['tag']==tag:
            actvgot=tag
            break
    if (probability<.88):
        actvgot='non'
    return(actvgot)  

def dontSearchyt(txt):
    # List of common "commanding" words to be removed
    commanding_words = ["play", "pause", "stop", "resume", "search", "google", "watch", "listen", "open", "go", "find", "show", "load", "start", "view", "playback"]

    ttxt=word_tokenize(txt)

    # Loop through the input words and add them to the filtered list if they are not in the commanding words list
    for word in ttxt:
        if word.lower() in commanding_words and word==ttxt[0]:
            txt.replace(word.lower(),"")
    if txt=='':
        txt=None
    return txt

def OpnYoutubeVid(vidname):

    # Create a YouTube Data API service instance
    youtube = build('youtube', 'v3', developerKey=YOU_API_KEY)

    # Input the search query
   
    if dontSearchyt(vidname):
        query = dontSearchyt(vidname)
    else :
        say("40o04")
    
    
    # Call the YouTube Data API to search for videos
    search_response = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=1
    ).execute()

    # Extract the video ID and title of the first result
    video_id = search_response['items'][0]['id']['videoId']
    video_title = search_response['items'][0]['snippet']['title']

    # Print the video title and URL
    say(f"Playing video: {video_title}")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    #say(f"Video URL: {video_url}")

    # Open the video URL in the default web browser
    webbrowser.open(video_url)
    
def OpnGoogle(query):
    Dntgogl(query)
    try:
        # Perform Google search
        url= f"https://www.google.com/search?q={query}"
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0"}
        page = requests.get(url,headers=headers)
        soup=BeautifulSoup(page.content,"html.parser")
        first_result = soup.find("div", {"class": "yuRUbf"}).a["href"]
        if first_result:
            # Open first search result in default web browser
            webbrowser.open(first_result)

            say(f"Successfully opened")# : {first_result}")
        else:
            say("No search results found.")
    except Exception as e:
        say(f"Error: {e}") 
    
def Dntgogl(query):
    """
    Removes common command phrases from a search query, but keeps them if needed.

    Args:
        query (str): The search query to process.

    Returns:
        str: The search query with command phrases removed.
    """
    # List of common command phrases
    command_phrases = [
        "get info on",
        "get information on",
        "search for",
        "google it",
        "google ",
        "google",
        "look up",
        "find out about",
        "tell me about",
        "tell me",
        "define",
        "explain",
        "what is",
        "how to",
        "where to",
        "when to",
        "why is",
        "who is",
        # Add more command phrases as needed
    ]

    # Iterate through the command phrases and remove them from the query
    for phrase in command_phrases:
        if phrase in query:
            query = query.replace(phrase, "").strip()

    return query
    
def opnstream(query):
    def extrctNofStreamer(txt):
        nonowrds=["twitch","youtube","stream","open","play","start","steam","sream","on"]
        c=[]
        txtt= word_tokenize(txt)
        for wrd in txtt:
            if wrd in nonowrds:
                txt=txt.replace(wrd, '')
            else:
                c.append(wrd)
        R=""
        for w in c:
            R=R.join(w)
        return R
    
    name=extrctNofStreamer(query)
    
    if ("youtube"in query) or("Youtube"in query) or("YOUTUBE"in query) :
        stream="youtube"
    elif ("twitch"in query) or("Twitch"in query) or("TWITCH"in query):
        stream="twitch"
    else:
        
        stream=qdb().get_question(f"where does {name} stream now?") 
        #print(f"where does {name} stream now?")
    if "youtube"in stream:
        OpnGoogle(f"{name} live on youtube")
    elif "twitch"in stream:
        OpnGoogle(f"{name} live on twitch")
    else:
        say("X_X")
    
def add_dairy(txt,title=None):
    notdairy=["write to diary", "save this story that happened to", "did i tell you what happened today in school"]
    
    for i in notdairy:
        if i in txt:
            txt=txt.replace(i,'')
    diarydb().add_diary_entry(txt,title)
  
def ksay(txt):
    #engine.say(txt)
    #engine.runAndWait()  
    sys.stdout.write(f'{txt}\n')
    sys.stdout.flush()
    
def say(txt):
    chatlog.insert_one({"added by": "A.S.H","text": txt,"time": datetime.now().isoformat()})
    kprint(txt)
    engine.say(txt)
    engine.runAndWait() 

def kinpkut(txt=''):
    if not txt in[""," "]:
        say(txt)
    u=sys.stdin.readline().strip()
    return u

def uinput(message=None):
    if message:
        say(message)
    k=True
    while k : 
        if kkiinput:
            k=False
    #while k:
    #    lastmessage = inputlog.find().sort('_id', -1).limit(1)
    #    c=[]
    #    for i in lastmessage:
    #        del i['_id']
    #        c.append(i)
    #    if not c== []:
    #        inputlog.delete_many({})
    #        k=False
    #        return c[0]['text']
    #    else:
    #        pass

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
        return ["_id",extract_id(txt)]
    else:
        return ["name",extract_full_name(txt)]

kparser=Sen()

def runn(message):
    mos=sent_tokenize(message)
    kl=[]
    typpropapilty=0
    emopropapilty=0
    ccc=0
    cmndpropapilty=0
    for message in mos:
        typclass=predict_class(message,commwords,commclasses,commmodle)
        emoclss=predict_class(message,emowords,emoclasses,emomodel)
        cmndclss=predict_class(message,cmndwords,cmndclasses,cmndmodle)
        
        
        #ints = predict_class(message)
        #typ=txtcllassfie(message, comms)
        typ = get_type(typclass,comms)
        typpropapilty=typpropapilty+float(typclass[0]['probability'])
        #print(kparser.get_subject(message),kparser.get_object(message))
        emo= get_emo(emoclss,emos)
        emopropapilty=emopropapilty+float(emoclss[0]['probability'])
        kl.append({"type":typ, "type propapilty": typpropapilty/ len(mos),'emotion': f'{emo}', 'emo propapilty': emopropapilty / len(mos)})

        if typ == "qustion":
            say('google it 4HEAD')
            if message[-1]in [" ",".","?"]:
                message=message.replace(message[-1], '')
            else:
                pass
            if message== '':
                say('invalid input..')
            else:
                answer = qdb().Get(message)
                if answer:
                    say(answer)
                    modee("ash")
        elif typ == "command":
            say("right away")
            ccc=+1
            cmnd = get_type(cmndclss,cmnds)
            cmndpropapilty=cmndpropapilty+float(cmndclss[0]['probability'])
            say(f'command: {cmnd}')
            say(f'propapilty: {cmndpropapilty/ccc }')
            if cmnd == "play youtube":
                OpnYoutubeVid(message)
            elif cmnd == "google it":
                OpnGoogle(message)
            elif cmnd=="open stream":
                opnstream(message)
            elif cmnd=="write to diary":
                add_dairy(message)
            else :
                say("^_^")
        else:
            say(typ)
            say(f'propapilty: {typpropapilty}')
    
        
    #autolrn(message,emo,'emo')
    #res = get_response(predict_class(message,intswords,intsclasses,chatbotints),intents)


#runn(sys.stdin.readline())


def modee(txt):
    mcount.find_one_and_replace({"no":2}, {"no":2,"modee":txt})
    
def qq(txt):
    mcount.find_one_and_replace({"no":3}, {"no":3,"q":txt})

def log(txt):
    # Create a new label widget
    chatLog.configure(state="normal")  # Enable editing temporarily
    chatLog.insert(tk.END, txt + "\n", "bold_font")  # Apply the "bold_font" tag to the inserted text
    chatLog.configure(state="disabled")  # Disable editing
    chatLog.see(tk.END)

    
def insertinput(text):
    chatlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})
    inputlog.insert_one({"added by": user,"text": text,"time": datetime.now().isoformat()})
    
def log_add(txt):
    formatted_time = datetime.now().isoformat()
    message = f"[{formatted_time}] {user}: {txt}"
    log(message)
    
def kprint(txt):
    formattedTime = datetime.now().isoformat()
    log(f'[{formattedTime}] A.S.H: {txt}')

def handle_keypress(event):
    if event.keysym == "Return":
        send_button.invoke()

def button_click():
    Modee=mcount.find_one({"no":2})["modee"]
    message = input_field.get().strip()
    input_field.delete(0, tk.END)
    if message != '':
        # Add the message to the chat log
        chatlog.insert_one({"added by": user,"text": message,"time": datetime.now().isoformat()})
        log_add(message)
        if Modee=="ash":
            runn(message)
        elif Modee=="isan":
            question=mcount.find_one({"no":3})["q"]
            answer=mcount.find_one({"no":4})["a"]
            if message in ["yah",'yes','of course','yup','yah','ya','yee','ye','idk','i dont know','i do not know']:
                qdb.add_question(question, answer[1],answer[2])
                say(answer[1])
                modee("ash")
            else:
                say("what is the right answer?")
                modee("isupq")
        elif Modee=="isupq":
            question=mcount.find_one({"no":3})["q"]
            if message in ["idk",'i dont know','i do not now','Idk',"IDK","I do not know","I dont know"]:
                say("answer was not found.")
                modee("ash")
            else:
                qdb.add_question(question,message,user)
                say ("question added to database.")
                modee("ash")
    else:
        log_add(message)

def get_lastmessage():
    lastmessage = chatlog.find().sort('_id', -1)
    c = {"lastmessages": []}
    for i in lastmessage:
        if i['added by'] == user:
            break
        del i['_id']
        c["lastmessages"].append(i)
    return jsonify(c)

root = tk.Tk()
root.title("A.S.H")
root.geometry("800x600")
root.iconbitmap(r"C:\Users\khaaf\Desktop\code\A.S.H\pyapp\ash_ai\icon.ico")

# Set the background color
root.configure(bg="#849bb1")

# Create the main container frame
maincon = tk.Frame(root, bg="#849bb1")
maincon.pack(fill="both", expand=True, pady=(0, 0))
maincon.grid_rowconfigure(0, weight=19)  # Set chat_log row weight to 19 (95%)
maincon.grid_rowconfigure(1, weight=1)  # Set botframe row weight to 1 (5%)
maincon.grid_columnconfigure(0, weight=1)  # Set column weight to 1

bold_font = font.Font(family="Arial", size=12, weight="bold")

# Create the chat log frame
#chatLog = scrolledtext.ScrolledText(maincon, bg="#042b46", fg="#FFFFFF", bd=0, state="disabled")
chatLog = tk.Text(maincon, bg="#042b46", fg="#FFFFFF", bd=0,state="disabled")
chatLog.tag_configure("bold_font", font=bold_font) 
chatLog.grid(row=0, column=0, sticky="nsew", padx=10,  pady=(0, 10))

# Create the bot frame
botframe = tk.Frame(maincon, bg="#849bb1")
botframe.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 25))

# Create the input frame
input_frame = tk.Frame(botframe, bg="#849bb1")
input_frame.pack(pady=0)

# Create the input field
input_field = tk.Entry(input_frame, bg="#042b46", fg="#FFFFFF")
input_field.pack(side="left", padx=10, ipadx=200,ipady=2.5)  # Increase the ipadx value to make the input field longer
input_field.bind("<Return>", handle_keypress) 

# Create the send button
modee("ash")

send_button = tk.Button(input_frame, text="Send", bg="#042b46", fg="#FFFFFF", bd=0, command=button_click,textvariable=modee)
send_button.pack(side="right", padx=10, ipadx=10,ipady=2.5)

# Add your code here to run within the main loop
log("ash is up!")
        
root.mainloop()


