import json

with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/command.json','r') )as f:
    commands=json.load(f)
    

def addpat(tag):
    pt=True
    for command in commands['command']:
        if command['tag']==tag:
            while (pt):
                patt= input(f'add a pattern for {command["tag"]}: \n>> ')
                if patt == 'quit':
                    pt=False
                elif patt == '':
                    pass
                else:
                    command['patterns'].append(patt)

def addcommand(cata):
    if cata == '':
        print('sorry wrong input :(')
    else:
        l=[]
        for i in commands['command']:
            l.append(i['tag'])
        if (cata not in l) :
            commands['command'].append({'tag':cata,"patterns":[]})
        
print(commands)
x= input('input "add" to add new command or "addpt" to add pattern to the existing command\n>> ')
if x=='add':
    tagg=input('input the name of the command that you want to add\n>> ')
    addcommand(tagg)
    addpat(tagg)
elif x=='addpt':
    taj=input('input the name of the command that you want to add patterns to \n>> ')
    addpat(taj)     
else:
    print('sorry wrong input :(')
   
   
with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/command.json','w')) as file:
                json.dump(commands,file,indent=6)
              