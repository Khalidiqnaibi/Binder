import json

with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/comm.json','r') )as f:
    comms=json.load(f)


for inte in comms['intents']:
    patt= input(f'add a pattern for {inte["tag"]}: \n>> ')
    inte['patterns'].append(patt)





with (open('C:/Users/khaaf/Desktop/code/ash_app/src/ash_ai/comm.json','w')) as file:
                json.dump(comms,file,indent=6)