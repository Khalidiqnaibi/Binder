import json

with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/emo.json','r') )as f:
    emos=json.load(f)

with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/intents.json','r') )as f:
    ints=json.load(f)
    
def lrnints(res,tag,emo):
    ints['intents'][tag]['responses'][emo].append(res)
    print ('thanks for helping to improve project ash :)')
    with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/intents.json','w')) as file:
        json.dump(ints,file,indent=6)
     
def emoadd():
    emo=[]
    for i in emos['intents']:
        emo.append(i['tag'])
    for j in  ints['intents'] :
        for t in emo :
            if t not in j['responses']:
                j['responses'].update({t:[]})
    with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/intents.json','w')) as file:
                json.dump(ints,file,indent=6)    

       
def addtg():
    k=True  
    tag=input('input tag \n>> ') 
    patterns=[]
    t=True
    while (k):
        pt=input('input pattern..if you want to stop type "quit" \n>> ')
        if pt == "quit":
            for i in emos['intents']:
                if tag==i['tag']:
                    t=False
                    for j in patterns:
                        i['patterns'].append(j)
                else:
                    pass    
            if t:        
                emos['intents'].append({"tag":tag,"patterns":patterns})
            print ('thanks for helping to improve project ash :)')
            with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/emo.json','w')) as file:
                json.dump(emos,file,indent=6)
            emoadd()
            k= False
        else:
            patterns.append(pt)
            
def addemo():
    k=True  
    t=True
    while (k):
        pt=input('input pattern..if you want to stop type "quit" \n>> ')
        if pt == "quit":
            emoadd()
            k= False
        else:
            tag=input('input tag \n>> ')
            for i in emos['intents']:
                if tag==i['tag']:
                    t=False
                    i['patterns'].append(pt)
                else:
                    pass    
            if t:        
                emos['intents'].append({"tag":tag,"patterns":[pt]})
            print ('thanks for helping to improve project ash :)')
            with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/emo.json','w')) as file:
                json.dump(emos,file,indent=6)
            
def addpat(tag):
    k=True
    patterns=[]
    t=True
    while (k):
        pt=input('input pattern..if you want to stop type "quit" \n>> ')
        if pt == "quit":
            for i in emos['intents']:
                if tag==i['tag']:
                    t=False
                    for j in patterns:
                        i['patterns'].append(j)
                else:
                    pass    
            if t:        
                emos['intents'].append({"tag":tag,"patterns":patterns})
            print ('thanks for helping to improve project ash :)')
            with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/emo.json','w')) as file:
                json.dump(emos,file,indent=6)
            k= False
        else:
            patterns.append(pt)
   

        
x= input('input "add" to add patterns and thier tag or "addtg" to add emotion or "addpt" to add pattern to an existing emotion \n>> ')
if x=='add':
    addemo()
elif x=='addpt':
    addpat(input('input the tag that you want to add to  \n>> '))     
elif x=='addtg':
    addtg()    
else:
    print('sorry wrong input :(')
   