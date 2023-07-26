from ash_ai.ash import runn
import tkinter as tk
from tkinter import Image, Image, font,PhotoImage
from datetime import datetime
import pymongo


user="khalid afif sami iqnaibi"

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["knowledge_db"]
inputlog=mydb["inputlog"]
chatlog=mydb['chatlog']
change =mydb['changes']
mcount=mydb["messagecount"]

def log(txt):
    # Create a new label widget
    chatLog.configure(state="normal")  # Enable editing temporarily
    chatLog.insert(tk.END, txt + "\n")
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
    message = input_field.get().strip()
    input_field.delete(0, tk.END)
    if message != '':

        # Add the message to the chat log
        log_add(message)

        # Send a POST request to the backend API
        insertinput(message)
    else:
        log_add(message)

def update_function():
    runn()

    # Call the update_function() again after a delay (in milliseconds)
    root.after(1000, update_function)

root = tk.Tk()
root.title("A.S.H")
root.geometry("800x600")

# Set the background color
root.configure(bg="#849bb1")

# Create the main container frame
maincon = tk.Frame(root, bg="#849bb1")
maincon.pack(fill="both", expand=True, pady=(0, 0))
maincon.grid_rowconfigure(0, weight=19)  # Set chat_log row weight to 19 (95%)
maincon.grid_rowconfigure(1, weight=1)  # Set botframe row weight to 1 (5%)
maincon.grid_columnconfigure(0, weight=1)  # Set column weight to 1

bold_font = font.Font(family="Arial", size=100, weight="bold")

# Create the chat log frame
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
send_button = tk.Button(input_frame, text="Send", bg="#042b46", fg="#FFFFFF", bd=0, command=button_click)
send_button.pack(side="right", padx=10, ipadx=10,ipady=2.5)

# Add your code here to run within the main loop
update_function()

root.mainloop()
