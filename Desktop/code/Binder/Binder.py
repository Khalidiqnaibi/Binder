import tkinter as tk
from tkinter import filedialog
import os
import shutil
import sqlite3
import sys
from datetime import date, timedelta,datetime
from sqlite3 import Error
from tkinter import PhotoImage
import speech_recognition as sr
from PIL import Image, ImageTk, ImageFilter
from nltk import clean_url, chain, text, word_tokenize,sent_tokenize
from tkcalendar import DateEntry
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from tkinter import ttk,font
import locale
from babel import numbers
import json
import time
import http.server
import socketserver
from tkinter import messagebox
import paypalrestsdk
import webbrowser
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
import requests

# code by Khalid Afif Iqnaibi
'''
    og code was coded 99% in python by Khalid Afif Iqnaibi 9/23 - 11/23
    finished v1.0 in 25/11/2023
    the online server added at 28/11/2023
    

'''
class MainClass:
    def __init__(self):
        self.apiurl='http://riasoftware.pythonanywhere.com'
        self.cname='RiaSoftware'
        self.appname='Binder'
        self.db_file = f'c:/{self.cname}/{self.appname}/db.sqlite'
        self.appPrice=200
        self.password = "@Ksoftkhaafif1"  # Change this to your secure password
        self.internet=True
        self.lsss = [
            ("oil_type", "Oil Type"),
            ("oil_filter", "Oil Filter Type"),
            ("air_filter", "Air Filter Type"),
            ("diesel_filter", "Diesel Filter"),
            ("gas_filter", "Gas Filter"),
            ("wipers", "Car Wipers"),
            ("front_break", "Front Break"),
            ("back_break", "Back Break"),
            ("timing_belt", "Timing Belt"),
            ("ac_filter", "AC Filter"),
        ]
        if not os.path.exists(self.db_file):
            with sqlite3.connect(self.db_file) as conn:
                self.makedb()
        self.fernet = self.create_fernet()
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        self.create_connection()
        self.conn = self.create_connection()
        self.entry_widgets = {}
        self.payed=True
        self.text_vars={}
        self.fmore=["oil_type","oil_filter", "air_filter","diesel_filter", "gas_filter","wipers","front_break","back_break","timing_belt","ac_filter"]
        self.fless={}
        self.current_value=1
        for i in self.lsss:
            self.fless[i[0]]=i[1]
        
        self.fss={}
        for i in self.lsss:
            self.fss[i[1]]=i[0]
        
        self.ki={}
        self.si={}
        self.tldb=''
        for k in self.fless:
            self.ki[k]=self.get_skinds_by_no(k)
            self.si[k]=self.get_skinds_by_no(k)
        self.plate='774-78-000'
        self.visits=self.get_all_visits_for_car(self.plate)
        self.is_user_input=True
            
        self.oauth_callback_port = 8080  # Set the port for the callback server
        self.client = WebApplicationClient("1068122250359-kmc7dsnfog76cp1oc2j1dhf1e4qjtcnf.apps.googleusercontent.com")
        
        self.initialize_gui()
        
        app_data=self.load_app_data()
        self.check_app_payment()
        self.plan=app_data['plan']
        if not self.plan in ['basic']:
            self.current_page = self.create_home_page(self.root,self.load_user_data(),app_data)
            self.show_page("home")
        else:
            self.current_page = self.create_adc_page(self.root,app_data)
            self.show_page("addcar") 

    def initialize_gui(self):
        self.root = tk.Tk()
        self.root.title(self.appname)
        self.root.geometry("800x600+220+10")
        
        temp_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(temp_dir, 'favicon.ico')
        self.root.iconbitmap(icon_path)
        self.root.minsize(800, 600)
        
        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)

        # Create a File menu with sub-items
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Account",font=font.Font(family="Arial", size=12), command=lambda: self.show_page("home"))
        file_menu.add_separator()
        file_menu.add_command(label="Home",font=font.Font(family="Arial", size=12),command=lambda: self.show_page("addcar"))
        file_menu.add_command(label="Search",font=font.Font(family="Arial", size=12),command=lambda: self.show_page("srch"))
        file_menu.add_command(label="Edit",font=font.Font(family="Arial", size=12),command=lambda: self.show_page('editkinds'))
        file_menu.add_separator()
        file_menu.add_command(label="Stats",font=font.Font(family="Arial", size=12),command=lambda: self.show_page("stats"))

        # Add the menus to the menu bar
        self.menu_bar.add_cascade(label="☰", menu=file_menu)
        #self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Set the menu bar for the root window
        self.root.config(menu=self.menu_bar)

        self.pages = {
            "home":1, #self.create_home_page(self.root,self.load_user_data()),
            "stats":2, #self.create_settings_page(self.root,self.load_user_data()),
            "cars":3, #self.create_dc_page(self.root,self.load_user_data()),
            "addcar":4, #self.create_adc_page(self.root,self.load_user_data()),
            'editkinds':5, #self.create_editkinds_page(self.root,self.load_user_data())
        }
        
    def show_page(self, page_name):
        user_data=self.load_user_data()
        app_data=self.load_app_data()
        self.plan=app_data['plan']
        trial_days_left = self.calculate_trial_days_left(app_data["first"])
        if not self.internet or page_name == 'int':
            self.current_page.pack_forget()
            self.modo="int"
            self.current_page = self.create_internet_page(self.root)
            self.current_page.pack()
            self.current_page.pack(expand=True, fill="both")
            self.root.configure(bg=f"{self.rgb_to_hex(255,255,255)}") 
        elif page_name == 'sup':
            self.current_page.pack_forget()
            self.modo="SU"
            self.current_page = self.create_subscription_page(self.root,user_data)
            self.current_page.pack()
            self.current_page.pack(expand=True, fill="both")
            self.root.configure(bg=f"{self.rgb_to_hex(255,255,255)}") 
        else:
            if not self.plan == "free" or trial_days_left > 0:
                if page_name == 'home':
                    self.current_page.pack_forget()
                    self.modo="h"
                    self.current_page = self.create_home_page(self.root,user_data,app_data)
                    self.current_page.pack()
                    self.current_page.pack(expand=True, fill="both")
                    self.root.configure(bg=f"{self.rgb_to_hex(255,255,255)}") 
                elif page_name == 'stats':
                    if self.current_page == self.create_dc_page(self.root,user_data):
                        self.up_all_dbt()
                    self.modo="s"
                    self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}") 
                    self.current_page.pack_forget()
                    self.current_page = self.create_settings_page(self.root,user_data)
                    self.current_page.pack()
                elif page_name == 'cars':
                    self.visits=self.get_all_visits_for_car(self.plate)
                    self.modo="v"
                    self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}")
                    self.current_page.pack_forget()
                    self.current_page = self.create_dc_page(self.root,user_data)
                    self.current_page.pack()
                    self.current_page.pack(expand=True, fill="both")
                elif page_name == 'srch':
                    self.modo="srch"
                    self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}")
                    self.current_page.pack_forget()
                    self.current_page = self.create_srch_page(self.root,user_data)
                    self.current_page.pack()
                    self.current_page.pack(expand=True, fill="both")
                elif page_name == 'addcar':
                    self.modo="a"
                    self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}")
                    self.current_page.pack_forget()
                    self.current_page = self.create_adc_page(self.root,user_data)
                    self.current_page.pack()
                    self.current_page.pack(expand=True, fill="both")
                elif page_name == 'editkinds':
                    self.current_page.pack_forget()
                    self.modo="e"
                    self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}")
                    self.current_page = self.create_editkinds_page(self.root,user_data)
                    self.current_page.pack()
                    self.current_page.pack(expand=True, fill="both")
                else:
                    self.current_page.pack_forget()
                    self.current_page = self.create_home_page(self.root,user_data)
                    self.current_page.pack()
            else:
                self.current_page.pack_forget()
                self.modo="h"
                self.root.configure(bg=f"{self.rgb_to_hex(255,255,255)}") 
                self.current_page = self.create_home_page(self.root,user_data,app_data)
                self.current_page.pack()
                self.current_page.pack(expand=True, fill="both")
                
    def create_home_page(self, parent, user_data, app_data):
        home_page = tk.Frame(parent)
    
        # Set the background image for the Home Page frame
        background_image_path = "home.jpg"
        background_image = Image.open(background_image_path)
        resized_width = 1300
        resized_height = 1000
        background_image = background_image.resize((resized_width, resized_height))
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(home_page, image=background_photo)
        background_label.photo = background_photo  # Keep a reference to avoid garbage collection
        background_label.place(relwidth=1, relheight=1)
    
        color = f"{self.rgb_to_hex(139,140,142)}"
        
        
        bd = tk.Frame(home_page,bg=f"{self.rgb_to_hex(0, 0, 0)}")
        bd.pack()
        
        home_frame = tk.Frame(bd, bg=color)
        home_frame.pack(pady=(0,1),padx=1)
    
        home_label = tk.Label(home_frame, text="Account", font=("Arial", 24), bg=color)
        home_label.pack(pady=30)
    
        if not user_data['name'] in ["non"]:
            user_name = user_data['name']
            if self.plan == "free":
                trial_days_left = self.calculate_trial_days_left(app_data["first"])
                if trial_days_left > 0:
                    trial_status = f"Trial ends in {trial_days_left} days"
                else:
                    trial_status = "Trial has ended\n Please pay to continue using the app"
    
                user_label = tk.Label(home_frame, font=("Arial", 14), text=f"Welcome, {user_name}", bg=color)
                trial_label = tk.Label(home_frame, font=("Arial", 14), text=trial_status, bg=color)
    
                user_label.pack(padx=20, pady=(50,45))
                trial_label.pack(padx=20, pady=(5,70))
                btns = tk.Frame(home_frame, bg=color)
                btns.pack()

                sup = ttk.Button(btns, text="Get full version", command=self.subbasic)
                sup.pack(side=tk.LEFT, padx=(40,5),pady=20)
                signup_button = ttk.Button(btns, text="Switch account", command=self.open_google_signup)
                signup_button.pack(side=tk.LEFT, padx=(5,40),pady=20)
            else:
                trial_status = "Thank you for supporting us"
    
                user_label = tk.Label(home_frame, font=("Arial", 14), text=f"Welcome, {user_name}", bg=color)
                trial_label = tk.Label(home_frame, font=("Arial", 14), text=trial_status, bg=color)
    
                user_label.pack(padx=20, pady=(50,45))
                trial_label.pack(padx=20, pady=(5,70))
                btns = tk.Frame(home_frame,bg=color)
                btns.pack(pady=10)
                
                backup_button = tk.Button(btns, text="Backup Database", command=self.backup_database)
                backup_button.pack(side=tk.LEFT, padx=(40,5),pady=20)
                signup_button = tk.Button(btns, text="Switch account", command=self.open_google_signup)
                signup_button.pack(side=tk.LEFT, padx=(5,40),pady=20)
                self.ldb=tk.Label(home_frame, font=("Arial", 14), text=self.tldb, bg=color)
                self.ldb.pack(pady=(0,20))
        else:
            user_label = tk.Label(home_frame, font=("Arial", 14), text="Please sign up with Google", bg=color)
            user_label.pack(padx=20, pady=120)
            open_button = tk.Button(home_frame, text="Sign Up with Google", command=self.open_google_signup)
            open_button.pack(padx=20, pady=20)
        self.tldb=''
        return home_page
    
    def backup_database(self):
        try:
            # Get the database content as JSON
            db_content = self.get_db_content_as_json()

            # Send the JSON data to the API for backup
            # Replace 'your_api_endpoint' with the actual endpoint where you want to send the data
            api_endpoint = f'{self.apiurl}/backup_database'
            response = requests.post(api_endpoint, json=db_content)

            if response.status_code == 200:
                self.tldb="Database backup successful!"
                self.show_page("home")
            else:
                self.tldb=f"Error backing up database. Status code: {response.status_code}"
                self.show_page("home")
        except Exception as e:
            print(f"Error during database backup: {e}")
            
    def get_db_content_as_json(self):
        # Replace 'path_to_your_db' with the actual path to your SQLite database file
        db_path = f'c:/{self.cname}/{self.appname}/db.sqlite'

        # Read the SQLite database and convert it to JSON (replace this logic with your actual conversion)
        with open(db_path, 'r', encoding='latin-1') as file:
            db_content = {"db": file.read()}

        return db_content

    def subbasic(self):
        webbrowser.open(self.apiurl+"/basic_sub")

    def open_google_signup(self):
        webbrowser.open(self.apiurl+"/logme")
    
    def check_app_payment(self):
        app_data = self.load_app_data()

        user_data = self.load_user_data()
        if app_data["payed"]:
            self.payed=True
        else:
            user_paid = user_data.get("payed", 0) >  (self.appPrice-1)

            if user_paid:
                app_data["payed"] = True
                self.payed=True
            else:
                self.payed=False

            txt=f"C:/{self.cname}/{self.appname}/data.txt"
            
            with open(txt, 'wb') as txt_file:
                encrypted_data = self.encrypt_data(app_data)
                txt_file.write(encrypted_data)
        
        return app_data
    
    def create_fernet(self):
        # Derive a key from the password using PBKDF2HMAC
        password = self.password.encode()
        salt = b"MY_Potatolikesme_too"  # Change this to a unique salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=100000,  # Adjust the number of iterations as needed
            salt=salt,
            length=32  # The length of the derived key
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))

        return Fernet(key)

    def encrypt_data(self, data):
        return self.fernet.encrypt(json.dumps(data).encode())

    def decrypt_data(self, encrypted_data):
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        except InvalidToken:
            # Handle decryption failure (e.g., incorrect password or corrupted data)
            return None

    def load_user_data(self):
        path = f"C:/{self.cname}/{self.appname}/user_data.txt"

        user_data = {
            "first": datetime.now().date().isoformat(),
            "google_id": 1,
            "name": "non",
            "payed": 0,
            'plan':'free'
        }

        if not os.path.exists(f"C:/{self.cname}"):
            os.makedirs(f"C:/{self.cname}")

        if not os.path.exists(f"C:/{self.cname}/{self.appname}"):
            os.makedirs(f"C:/{self.cname}/{self.appname}")

        if path and os.path.exists(path):
            with open(path, "rb") as txt_file:
                encrypted_data = txt_file.read()
                user_data = self.decrypt_data(encrypted_data)
        else:
            with open(path, "wb") as txt_file:
                encrypted_data = self.encrypt_data(user_data)
                txt_file.write(encrypted_data)
        if user_data['name'] in ['non']:
            app_data = self.load_app_data()
            jid={'id':app_data['google_id']}
            response = requests.post(f'{self.apiurl}/usr_me', json=jid)
            if response.status_code == 200:
                user_data=response.json()
                with open(path, "wb") as txt_file:
                    encrypted_data = self.encrypt_data(user_data)
                    txt_file.write(encrypted_data)
            else:
                pass#user_me
        if user_data['plan']in['free']:
            try:
                response = requests.get(f'{self.apiurl}/plan_me')#, timeout=0.5)
                if response.status_code == 200:
                    c=response.json()
                    user_data['plan']=c['plan']
                    user_data['payed']=c['payed']
                    app_data=self.app_data_me()
                    with open(path, "wb") as txt_file:
                        encrypted_data = self.encrypt_data(user_data)
                        txt_file.write(encrypted_data)
                else:
                    pass#plan_me
            except Exception as e:
                pass
        if 'db' in user_data:
            with open(f"C:/{self.cname}/{self.appname}/db.sqlite", 'w',encoding='latin-1') as ddb:
                ddb.write(user_data['db'])
            raw=user_data
            d={}
            for i in raw:
                if not i == 'db':
                    d[i]=user_data[i]
            
            with open(path, 'wb') as file:
                encrypted_data = self.encrypt_data(d)
                file.write(encrypted_data)

            user_data=d
        return user_data

    def load_app_data(self):
        app_data_path = f"C:/{self.cname}/{self.appname}/data.txt"

        if not os.path.exists(f"C:/{self.cname}"):
            os.makedirs(f"C:/{self.cname}")

        if not os.path.exists(f"C:/{self.cname}/{self.appname}"):
            os.makedirs(f"C:/{self.cname}/{self.appname}")

        if not os.path.exists(app_data_path):
            app_data=self.app_data_me()
        else:
                
            with open(app_data_path, 'rb') as txt_file:
                encrypted_data = txt_file.read()
                app_data = self.decrypt_data(encrypted_data)
                
            self.apiurl = app_data.get('url', '')  # Assuming 'url' might not always be present
        if app_data['google_id'] in [1]:
            app_data=self.app_data_me()
        return app_data
    
    def app_data_me(self):
        try:
            # Attempt to make a request
            response = requests.get(f'{self.apiurl}/app_data_me')
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            self.internet=True
            app_data = response.json()
            with open(f"C:/{self.cname}/{self.appname}/data.txt", 'wb') as txt_file:
                encrypted_data = self.encrypt_data(app_data)
                txt_file.write(encrypted_data)
            self.apiurl = app_data.get('url', '')  # Assuming 'url' might not always be present
            # If the request is successful, print the result
            return app_data
        except requests.exceptions.RequestException as e:
            self.internet=False
            print(f"Failed to make the request: {e}")
            return None
        
    def db_me(self):
        idd=self.load_app_data()['google_id']
        jid={'id':idd}
        response = requests.post(f'{self.apiurl}/db_me', json=jid)
        db = response.json()
        with open(f"C:/{self.cname}/{self.appname}/db.sqlite", 'r',encoding='latin-1') as ddb:
            ddb.write(db)
    
    def calculate_trial_days_left(self, first_date_str):
        try:
            first_date = datetime.strptime(first_date_str, "%Y-%m-%d")
            today = datetime.now()
            trial_duration = timedelta(days=7)
            trial_end_date = first_date + trial_duration
            days_left = (trial_end_date - today).days
            return max(0, days_left)
        except ValueError:
            return 0
    
    def rgb_to_hex(self,r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_connection(self):
        conn = sqlite3.connect(self.db_file)
        return conn

    def fetch_data(self,query, data=None):
        conn = self.create_connection()
        cur = conn.cursor()
        if data:
            cur.execute(query, data)
        else:
            cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return rows
    
    def create_visitstable(self):
        conn = self.create_connection()
        query = f"""
        CREATE TABLE IF NOT EXISTS visits (
            avno INTEGER PRIMARY KEY AUTOINCREMENT,
            vno INTEGER,
            date TEXT,
            chkup TEXT,
            counter INTEGER,
            fcounter INTEGER,
            distance INTEGER,
            oil_type TEXT,
            oil_filter TEXT,
            air_filter TEXT,
            diesel_filter TEXT,
            ac_filter TEXT, 
            gas_filter TEXT,
            wipers TEXT,
            front_break TEXT,
            back_break TEXT,
            timing_belt TEXT,
            coast INTEGER,
            payed INTEGER,
            debit INTEGER,
            details TEXT,
            lplate TEXT,
            FOREIGN KEY (lplate) REFERENCES cars (lplate)
                );
        """
        self.execute_query(conn, query)
    
    def create_carstable(self):
        conn = self.create_connection()
        query = f"""
        CREATE TABLE IF NOT EXISTS cars (
        cfno INTEGER PRIMARY KEY AUTOINCREMENT,
        lplate TEXT,
        model TEXT,
        phone INTEGER,
        email TEXT,
        gastyp TEXT,
        payed INTEGER,
        debit INTEGER,
        lvno INTEGER,
        idNo INTEGER,
        FOREIGN KEY (idNo) REFERENCES owners (idNo)
        );
        """
        self.execute_query(conn, query)
    
    def create_ownerstable(self):
        conn = self.create_connection()
        query = f"""
        CREATE TABLE IF NOT EXISTS owners (
        idNo INTEGER PRIMARY KEY,
        name TEXT,
        phone INTEGER,
        email TEXT
        );
        """
        self.execute_query(conn, query)
    
    def create_kindstable(self):
        name="kinds"
        conn = self.create_connection()
        query = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            kno INTEGER PRIMARY KEY AUTOINCREMENT,
            cname TEXT,
            dname TEXT
                );
        """
        self.execute_query(conn, query)
    
    def create_skindstable(self):
        name="skinds"
        conn = self.create_connection()
        query = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            sno INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            kno INTEGER,
            FOREIGN KEY (kno) REFERENCES kinds (kno)
                );
        """
        self.execute_query(conn, query)
    
    def mkinds(self,lsss=[
        ("oil_type", "Oil Type"),
        ("oil_filter", "Oil Filter Type"),
        ("air_filter", "Air Filter Type"),
        ("diesel_filter", "Diesel Filter"),
        ("gas_filter", "Gas Filter"),
        ("wipers", "Car Wipers"),
        ("front_break", "Front Break"),
        ("back_break", "Back Break"),
        ("timing_belt", "Timing Belt"),
        ("ac_filter", "AC Filter"),]):

        fmore=[]
        for i in lsss:
            fmore.append({"cname":i[0],"dname":i[1]})

        jj=1
        for i in fmore:
            self.insert_or_update_data_to_kinds(i)
            self.insert_or_update_data_to_skinds({"name":"No Change","price":0,'kno':jj})
            self.insert_or_update_data_to_skinds({"name":"New","price":0,'kno':jj})
            jj+=1
    
    def create_varstable(self):
        name="vars"
        conn = self.create_connection()
        query = f"""
            CREATE TABLE IF NOT EXISTS vars (
            no INTEGER PRIMARY KEY AUTOINCREMENT,
            val INTEGER,
            name TEXT
            );
        """
        self.execute_query(conn, query)
    
    def makedb(self):
        self.create_ownerstable()
        self.create_visitstable()
        self.create_kindstable()
        self.create_skindstable()
        self.create_carstable()
        self.create_varstable()
        self.mkinds(self.lsss)

    def get_car_by_no(self,lplate):
        query = "SELECT * FROM cars WHERE lplate = ?"
        data = self.fetch_data(query, (lplate,))
        if data:
            i={
                "lplate": data[0][0],
                "model": data[0][1],
                "phone": data[0][2],
                "email": data[0][3],
                "gastyp": data[0][4],
                "payed": data[0][5], 
                "debit": data[0][6],
                "idNo" : data[0][7] 
            }
            return i
        else:
            return None
 
    def get_visit_by_date(self,date,lplate):
        query = "SELECT * FROM visits WHERE date = ? AND lplate = ?"
        data = self.fetch_data(query, (date,lplate,))
        if data:
            i={
                "avno":data[0][0],
                "vno": data[0][1],
                "date": data[0][2],             
                "chkup": data[0][3],
                "counter": data[0][4],
                "fcounter": data[0][5],
                "distance": data[0][6],
                "oil_type": data[0][7],
                "oil_filter": data[0][8],
                "air_filter": data[0][9],              
                "diesel_filter": data[0][10],             
                "ac_filter": data[0][11], 
                "gas_filter": data[0][12],
                "wipers" : data[0][13] ,      
                "front_break": data[0][14],   
                "back_break": data[0][15],      
                "timing_belt": data[0][16],       
                "coast":data[0][17],       
                "payed": data[0][18],  
                "debit": data[0][19], 
                "details": data[0][20],   
                "lplate": lplate  
            }
            return i
        else:
            return None
 
    def get_owner_by_no(self,id_no):
        query = "SELECT * FROM owners WHERE idNo = ?"
        data = self.fetch_data(query, (id_no,))
        if data:
            i={
                "idNo": data[0][0],
                "name": data[0][1],
                "phone": data[0][2],
                "email": data[0][3], 
            }
            return i
        else:
            return None 

    def get_all_cars_for_id(self,idno):
        conn=self.create_connection()
        query = "SELECT * FROM owners WHERE idNo = ?"
        result = self.fetch_data(query, (idno,))
        if result: 
            update_query = "SELECT * FROM cars WHERE idNo = ?"
            data = self.fetch_data(update_query, (idno,))
            return data
        else:
            return 'No user for this Id number.'

    def get_all_visits_for_car(self,lplate):
        conn=self.create_connection()
        query = "SELECT * FROM cars WHERE lplate = ?"
        result = self.fetch_data(query, (lplate,))
        if result: 
            update_query = "SELECT * FROM visits WHERE lplate = ?"
            datas = self.fetch_data(update_query, (lplate,))
            if datas:
                i=[]
                for data in datas :
                    i.append({
                        "avno":data[0],
                        "vno": data[1],
                        "date": data[2],             
                        "chkup": data[3],
                        "counter": data[4],
                        "fcounter": data[5],
                        "distance": data[6],
                        "oil_type": data[7],
                        "oil_filter": data[8],
                        "air_filter": data[9],              
                        "diesel_filter": data[10],             
                        "ac_filter": data[11], 
                        "gas_filter": data[12],
                        "wipers" : data[13] ,      
                        "front_break": data[14],   
                        "back_break": data[15],      
                        "timing_belt": data[16],       
                        "coast":data[17],       
                        "payed": data[18],  
                        "debit": data[19], 
                        "details": data[20],   
                        "lplate": lplate})
                popo = sorted(i, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
                return popo
            else:
                return None
        else:
            return 'No visits for this car.'

    def open_file(self):
        path = self.car_folder_path
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            os.makedirs(path)
            os.startfile(path)

    def get_kinds_by_name(self,name):
        query = "SELECT * FROM kinds WHERE cname = ?"
        data =self.fetch_data(query, (name,))
        if data:
            i={
                "kno": data[0][0],
                "cname": data[0][1],
                "dname": data[0][2],
            }
            return i
        else:
            return None 
    
    def get_skinds_by_no(self,name):
        kno=self.get_kinds_by_name(name)["kno"]
        query = "SELECT * FROM skinds WHERE kno = ?"
        data = self.fetch_data(query, (kno,))
        i=[]
        if data:
            for j in data:
                i.append({"sno": j[0],"name": j[1],"price": j[2],"kno":j[3]})
            return i
        else:
            return None 

    def update_entries(self, data):
        self.is_user_input=False
        self.update_var(3, 'val', 'true')
        for key, value in data.items():
            if key in self.entry_widgets:
                if key in ["chkup"]:  # Check if the key corresponds to the 'date' field
                    self.nxt_chkup.set_date(datetime.strptime(value, '%Y-%m-%d'))  # Set the date for the DateEntry widget
                elif key in ["date"]:  # Check if the key corresponds to the 'date' field
                    self.vd.set_date(datetime.strptime(value, '%Y-%m-%d')) 
                elif key in ["details"]:
                    self.entry_widgets[key].delete('1.0', tk.END)
                    self.entry_widgets[key].insert('1.0', str(value))
                elif key in self.fmore:
                    if not self.drop_vars == {}:
                        self.drop_vars[self.fless[key]].set(str(value))
                elif key in ["search"]:
                    self.entry_widgets[key].delete(0, tk.END)
                else:
                    self.entry_widgets[key].delete(0, tk.END)
                    self.entry_widgets[key].insert(0, str(value))

        patient_folder_path = self.create_date_folder(data['date'])
        self.is_user_input=True

    def create_car_folder(self,fname):
        c=os.path.join(os.path.expanduser("~"), "Desktop")
        script_dir = os.path.join(c,"cars_files")
        if not os.path.exists(script_dir):
            os.makedirs(script_dir)
        patient_folder_path = os.path.join(script_dir, fname)
        if not os.path.exists(patient_folder_path):
            os.makedirs(patient_folder_path)
        self.car_folder_path=patient_folder_path
        return patient_folder_path
    
    def create_date_folder(self,fname):
        fname=str(fname)
        c=os.path.join(os.path.expanduser("~"), "Desktop")
        script_dir = os.path.join(c,"cars_files")
        script_dirs = os.path.join(script_dir,f"{self.plate}")
        if not os.path.exists(script_dirs):
            os.makedirs(script_dirs)
        date_folder_path = os.path.join(script_dirs, fname)
        if not os.path.exists(date_folder_path):
            os.makedirs(date_folder_path)
        self.car_folder_path=date_folder_path
        return date_folder_path

    def parse_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, '%Y/%m/%d')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    except ValueError:
                        try:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                        except ValueError:
                            return None  # Invalid date format
        return date_obj.strftime('%Y-%m-%d')

    def search(self):
        # Get the date from the search widget text box
        date_to_search = self.entry_widgets["search"].get().strip()
        self.entry_widgets["search"].delete(0, tk.END)
        self.update_var(3, 'val', 'true')

        # Parse the date into a standardized format
        formatted_date = self.parse_date(date_to_search)

        if formatted_date is None:
            print("Invalid date format.")
            return
        
        result = self.get_visit_by_date(formatted_date,self.plate)

        if result:
            jk=0
            for i in self.visits:
                if i['avno'] == result['avno']:
                    self.update_curr(jk) 
                    break
                jk+=1
            self.update_entries(result)
            self.entry_widgets["search"].insert(0, f"{datetime.now().date()}")
        else:
            self.entry_widgets["search"].insert(0, f"{datetime.now().date()}")
            print( "Data not found for the entered date.")

    def update_current_value(self,new_value):
        self.current_value=new_value

    def update_var(self,no, field, value):
        query = f"UPDATE vars SET {field} = ? WHERE no = ?"
        self.execute_query(self.create_connection(), query, (value, no))

    def get_var_by_no(self,no,field):
        query = f"SELECT {field} FROM vars WHERE no = ?"
        result = self.fetch_data(query, (no,))
        if result:
            return result[0][0]
        else:
            return None

    def next_entry(self,event, entry_widget):
        if entry_widget in [self.entry_widgets[i] for i in ["counter", "fcounter", "distance", "coast", "payed", "debit", "details"]]:
            if entry_widget in [self.entry_widgets["search"], ]:
                self.search()
            elif isinstance(entry_widget, tk.Text) and "details" in self.entry_widgets:
                entry_widget.insert(tk.END, "\n")  # Insert a newline in the "details" text widget
            else:
                self.tacc(event)  # Update the data in MongoDB for the current entry

                # Check if the entry_widget is associated with a drop-down menu
                for label_text, kind_var in self.drop_vars.items():
                    if label_text in ['chkup','date']:
                        if entry_widget == self.entry_widgets[label_text]:
                            # Get the index of the current selection in the list of options
                            current_index = self.xx[label_text].index(kind_var.get())

                            # Increment the index to move to the next option
                            next_index = (current_index + 1) % len(self.xx[label_text])

                            # Set the next option as the selected value in the drop-down menu
                            kind_var.set(self.xx[label_text][next_index])
                    else:
                        if entry_widget == self.entry_widgets[self.fss[label_text]]:
                            # Get the index of the current selection in the list of options
                            current_index = self.xx[label_text].index(kind_var.get())

                            # Increment the index to move to the next option
                            next_index = (current_index + 1) % len(self.xx[self.fss[label_text]])

                            # Set the next option as the selected value in the drop-down menu
                            kind_var.set(self.xx[self.fss[label_text]][next_index])

                next_widget = event.widget.tk_focusNext()
                if isinstance(next_widget, tk.Button):
                    next_widget = next_widget.tk_focusNext()  # Skip the button and move to the next widget
                next_widget.focus()
    
    def get_v_by_no(self,vno,lplate):
        self.plate=lplate
        self.visits=self.get_all_visits_for_car(self.plate)
        if vno < 1:
            return None
        if not len(self.visits)<vno:
            x=self.visits[vno-1]
            return x
        else:
            return None
    
    def up_last(self):
        self.visits=self.get_all_visits_for_car(self.plate)
        x=self.visits[-1]
        return x

    def update_last(self,num):
        no= self.get_var_by_no(2,'val')
        self.update_var(2, "val", num) 

    def update_curr(self,num):
        self.current_value=num

    def mi_last(self):
        no= self.get_var_by_no(2,'val')
        self.update_var(2, "val", no-1) 

    def last(self):
        ch=len(self.visits)-1
        new_p = self.up_last()
        date = datetime.now().date().isoformat()
        if not new_p['date']== date:
            nn={
                "vno":ch,
                "date": date,
                "chkup": self.nxt_date_chkup().date().isoformat(),
                "counter": 0,
                "fcounter": 0,
                "distance": 0,
                "oil_type": 'No Change',
                "oil_filter": 'No Change',
                "air_filter": 'No Change',
                "diesel_filter": 'No Change',
                "ac_filter": 'No Change',
                "gas_filter": 'No Change',
                "wipers": 'No Change',
                "front_break": 'No Change',
                "back_break": 'No Change',
                "timing_belt": 'No Change',
                "coast": 0,
                "payed": 0,
                "debit":0,
                'details':'',
                "lplate": self.plate,
                }
            self.insert_or_update_data_to_visits(nn)
            self.update_entries(nn)
            new_p=nn
        if new_p:
            folder_path =self.create_date_folder(new_p['date'])

            self.update_curr(ch)
            self.update_entries(new_p)
        else:
            print(f"Data with no {ch} not found for the search entry.")
            
    def Blank(self):
        for key in self.entry_widgets:
            if key in ["details"]:
                self.entry_widgets[key].delete('1.0', tk.END)
            elif key in ["chkup"]:
                nxdate=date(2000, 6, 1)
                self.nxt_chkup.set_date(nxdate)
            elif key in ["date"]:
                nxdate=date(2000, 1, 1)
                self.vd.set_date(nxdate)
            elif key in self.fless and self.fless[key] in self.drop_vars:
                self.drop_vars[self.fless[key]].set(self.xx[key][0])
            elif key in ["search"]:
                pass
            else:
                self.entry_widgets[key].delete(0, tk.END)
                self.entry_widgets[key].insert(0, str(0))

    def first(self):
        no=1
        new_p = self.get_v_by_no(no,self.plate)
        if new_p:
            folder_path =self.create_date_folder(new_p['date'])
            self.update_curr(no)
            self.update_entries(new_p)
        else:
            print("Data not found for the search entry.")  

    def nextt(self):
        current_value =self.current_value
        new_value = current_value + 1
        new_p = self.get_v_by_no(new_value,self.plate)
        if new_p:
            folder_path =self.create_date_folder(new_p['date'])
            self.update_entries(new_p)
            self.update_current_value(new_value)
        else:
            date=datetime.now().date().isoformat()
            z=self.get_visit_by_date(date,self.plate)
            if not z:
                nn={
                        "vno":new_value,
                        "date": date,
                        "chkup": self.nxt_date_chkup().date().isoformat(),
                        "counter": 0,
                        "fcounter": 0,
                        "distance": 0,
                        "oil_type": 'No Change',
                        "oil_filter": 'No Change',
                        "air_filter": 'No Change',
                        "diesel_filter": 'No Change',
                        "ac_filter": 'No Change',
                        "gas_filter": 'No Change',
                        "wipers": 'No Change',
                        "front_break": 'No Change',
                        "back_break": 'No Change',
                        "timing_belt": 'No Change',
                        "coast": 0,
                        "payed": 0,
                        "debit":0,
                        'details':'',
                        "lplate": self.plate,
                    }
                self.insert_or_update_data_to_visits(nn)
                self.update_entries(nn)
                self.update_current_value(new_value)
            else:
                no = self.current_value
                nn = self.visits
                if not new_value>len(nn)+1:
                    self.update_current_value(new_value)
                
                self.Blank()
               
    def pervv(self):
        current_value = self.current_value
        new_value = current_value - 1
        if new_value<0:
            print("This is the first entry")
        else:
            new_p = self.get_v_by_no(new_value,self.plate)
            if new_p:
                self.update_entries(new_p)
                self.update_current_value(new_value)
    
    def kind_var_changed(self, kind, *args):
        price = 0
        for i in self.ki:
            if self.fless[i] in self.drop_vars:
                selected_option = self.drop_vars[self.fless[i]].get()
                cc = self.ki[i]
                for j in range(len(cc)):
                    if selected_option == cc[j]['name']:
                        price += cc[j]['price']

        if self.is_user_input:
            no = self.current_value
            nn = self.visits
            if no - 2 >= 0 and nn:
                nn = nn[no - 2]

        if 'coast' in self.entry_widgets:
            self.entry_widgets['coast'].delete(0, tk.END)
            self.entry_widgets['coast'].insert(0, str(price))
        
    def get_last_v_for_car(self,plate):
        query = "SELECT lvno FROM cars WHERE lplate = ?"
        result = self.fetch_data(query, (plate,))
        return result[0][0]
    
    def up_all_dbt(self):
        payed=0
        debit=0
        for i in self.visits:
            if not i['debit'] in ['',' ']:
                debit+=i['debit']
            if i['payed'] in [' ','']:
                payed+=i['payed']
        self.updt_debit(payed,debit)
    
    def updt_debit(self,payed,debit):
        query = "SELECT payed,debit FROM cars WHERE lplate = ?"
        r=self.fetch_data(query, (self.plate,))
        payedd = r[0][0]
        debitt = r[0][1]
        payed+=payedd
        debit+=debitt
        conn=self.create_connection()
        update_query = "UPDATE cars SET payed = ?,debit = ? WHERE lplate = ?"
        self.execute_query(conn, update_query, (payed,debit,self.plate))
    
    def create_adc_page(self,parent,user_data):
        self.ac_frame = tk.Frame(parent, bg=f"{self.rgb_to_hex(139,140,142)}")
        background_image_path = 'home.jpg'
        background_image = Image.open(background_image_path)
        resized_width = 1300
        resized_height = 1000
        background_image = background_image.resize((resized_width, resized_height))
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(self.ac_frame, image=background_photo)
        background_label.photo = background_photo  # Keep a reference to avoid garbage collection
        background_label.place(relwidth=1, relheight=1)
        bdo = tk.Frame(self.ac_frame,bg=f"{self.rgb_to_hex(0, 0, 0)}")
        bdo.pack(pady=(60,0))
        bd = tk.Frame(bdo,bg=self.rgb_to_hex(139,140,142))
        bd.pack(padx=1,pady=1)
        header_label = tk.Label(bd, text="Add A Car", font=("Arial", 30), bg=self.rgb_to_hex(139,140,142))
        header_label.pack(pady=(15,25))
        main_frame = tk.Frame(bd, bg=self.rgb_to_hex(139,140,142))
        main_frame.pack( pady=5,padx=20)
        
        lfields = [
            ("name", "Car Owner"),
            ("Id No","Id Number"),
            ("Phone No","Phone Number"),
            ("Email","Email"),
            ("No", "Car Number"),
            ("model", "Car Model")
        ]
        entry_widgets = {}
        
        dt={"lplate": "000-00-000",
            "model": "",
            "phone": 000000000,
            "email": "potato@gmail.com",
            "gastyp": "gas",
            "payed": 0, 
            "debit": 0,
            "lvno":1,
            "idNo" : 0}
        
        for i, (key, label_text) in enumerate(lfields):
            label = tk.Label(main_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i,sticky="w", column=2, padx=5, pady=5)

            entry = ttk.Entry(main_frame, width=20, font=("Arial", 10))
            entry.grid(row=i, column=3, padx=5, pady=5)
            entry_widgets[key] = entry
            
        fuel_type_options = ["Choose Fuel Type","Gasoline", "Diesel", "Electric", "Hybrid"]
        fuel_type_var = tk.StringVar(bd )
        fuel_type_var.set(fuel_type_options[0])  # Set the default value
        self.fuel_type_var=fuel_type_var
        fuel_type_menu = ttk.OptionMenu(bd , fuel_type_var, *fuel_type_options)
        fuel_type_menu.pack(pady=15)
        
        addcarbtn=ttk.Button(bd, text="Open", command=self.add_car)
        addcarbtn.pack(pady=5)
            
        self.acentry_widgets = entry_widgets
        self.acentry_widgets['No'].bind("<ButtonRelease-1>",self.err) 
        self.addcarinfo=dt
        return self.ac_frame    
    
    def create_internet_page(self,parent):
        self.i_frame = tk.Frame(parent, bg=f"{self.rgb_to_hex(139,140,142)}")
        background_image_path = 'home.jpg'
        background_image = Image.open(background_image_path)
        resized_width = 1300
        resized_height = 1000
        background_image = background_image.resize((resized_width, resized_height))
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(self.i_frame, image=background_photo)
        background_label.photo = background_photo  # Keep a reference to avoid garbage collection
        background_label.place(relwidth=1, relheight=1)
        bdo = tk.Frame(self.i_frame,bg=f"{self.rgb_to_hex(0, 0, 0)}")
        bdo.pack(pady=(60,0))
        bd = tk.Frame(bdo,bg=self.rgb_to_hex(139,140,142))
        bd.pack(padx=1,pady=1)
        
        label = tk.Label(bd, text='Failed to connect to the internet', font=("Arial", 15), bg=self.rgb_to_hex(139, 140, 142))
        label.pack(pady=(150,55),padx=5)
        
        addcarbtn=ttk.Button(bd, text="Refresh", command=self.refesh)
        addcarbtn.pack(pady=55)
        
        return self.i_frame   
    
    def refesh(self):
        app_data=self.app_data_me()
    
    def err(self,event):
        self.acentry_widgets['No'].delete(0, tk.END)

    def add_car(self):
        car_data = {
            'lplate': self.acentry_widgets['No'].get(),
            'model': self.acentry_widgets['model'].get(),
            'phone': self.acentry_widgets['Phone No'].get(),
            'email': self.acentry_widgets['Email'].get(),
            'gastyp': self.fuel_type_var.get(),
            'payed': 0,
            'debit': 0,
            'lvno': 1,
            'idNo': self.acentry_widgets['Id No'].get()
        }

        owner_data = {
            'name': self.acentry_widgets['name'].get(),
            'phone': self.acentry_widgets['Phone No'].get(),
            'email': self.acentry_widgets['Email'].get(),
            'idNo': self.acentry_widgets['Id No'].get()
        }
        if not car_data['lplate'] in ['',' ']:
            if not owner_data["phone"] in ['',' '] or not owner_data["phone"] in ['',' '] :
                query = "SELECT * FROM owners WHERE idNo = ?"
                result = self.fetch_data(query, (owner_data["idNo"],))
                query = "SELECT * FROM owners WHERE phone = ?"
                r=self.fetch_data(query, (owner_data["phone"],))
                if not r and not result:
                    self.insert_or_update_data_to_owners(owner_data)
             
            query = "SELECT * FROM cars WHERE lplate = ?"
            result = self.fetch_data(query, (car_data["lplate"],))
            if not result:
                self.plate=car_data['lplate']
                self.visits=self.get_all_visits_for_car(self.plate)
                self.insert_or_update_data_to_cars(car_data)
                nn={
                    "vno":1,
                    "date": datetime.now().date().isoformat(),
                    "chkup": self.nxt_date_chkup().date().isoformat(),
                    "counter": 0,
                    "fcounter": 0,
                    "distance": 0,
                    "oil_type": 'No Change',
                    "oil_filter": 'No Change',
                    "air_filter": 'No Change',
                    "diesel_filter": 'No Change',
                    "ac_filter": 'No Change',
                    "gas_filter": 'No Change',
                    "wipers": 'No Change',
                    "front_break": 'No Change',
                    "back_break": 'No Change',
                    "timing_belt": 'No Change',
                    "coast": 0,
                    "payed": 0,
                    "debit":0,
                    'details':'',
                    "lplate": self.plate,
                }
                self.update_current_value(1)
                self.insert_or_update_data_to_visits(nn)
                print("Car and owner added")
            else: 
                date=datetime.now().date().isoformat()
                self.plate=car_data['lplate']
                z=self.get_visit_by_date(date,self.plate)
                self.visits=self.get_all_visits_for_car(self.plate)
                vcv=self.get_last_v_for_car(self.plate)
                if not z:
                    nn={
                    "vno":vcv,
                    "date": date,
                    "chkup": self.nxt_date_chkup().date().isoformat(),
                    "counter": 0,
                    "fcounter": 0,
                    "distance": 0,
                    "oil_type": 'No Change',
                    "oil_filter": 'No Change',
                    "air_filter": 'No Change',
                    "diesel_filter": 'No Change',
                    "ac_filter": 'No Change',
                    "gas_filter": 'No Change',
                    "wipers": 'No Change',
                    "front_break": 'No Change',
                    "back_break": 'No Change',
                    "timing_belt": 'No Change',
                    "coast": 0,
                    "payed": 0,
                    "debit":0,
                    'details':'',
                    "lplate": self.plate,
                }
                    self.update_current_value(vcv)
                    self.insert_or_update_data_to_visits(nn)
                self.car_folder_path =self.create_date_folder(f'{date}')
            self.show_page("cars")
            self.last()
        else:
            z="please provide number."
            self.acentry_widgets['No'].insert(0, z)
            print(z)  
        
    def insert_or_update_data_to_kinds(self,data):
        conn=self.create_connection()
        query = "SELECT * FROM kinds WHERE cname = ?"
        result = self.fetch_data(query, (data["cname"],))
        if result: 
            update_query = "UPDATE kinds SET cname = ?,dname = ? WHERE kno = ?"
            self.execute_query(conn, update_query, (data['cname'],data['dname'],data['kno']))
        else:
            insert_query = f"INSERT INTO kinds (cname,dname) VALUES (?, ?)"
            self.execute_query(conn, insert_query, (data['cname'],data['dname']))
        
    def insert_or_update_data_to_skinds(self,data):
        conn=self.create_connection()
        if "sno" in data: 
            update_query = "UPDATE skinds SET name = ?,price = ? WHERE sno = ?"
            self.execute_query(conn, update_query, (data['name'],data['price'],data['sno']))
        else:
            insert_query = f"INSERT INTO skinds (name,price,kno) VALUES (?, ?, ?)"
            self.execute_query(conn, insert_query, (data['name'],data['price'],data['kno']))
            
    def create_dc_page(self,parent,user_data):
        self.C_frame = tk.Frame(parent, bg=self.rgb_to_hex(139,140,142))
        xx={}
        xp={}
        for k in self.ki:
            xx[k]=[l["name"] for l in self.ki[k]]
            xp[k]=[l["price"] for l in self.ki[k]]
        self.xx=xx
        self.xp=xp 

        main_frame = tk.Frame(self.C_frame, bg=self.rgb_to_hex(139,140,142))
        main_frame.pack(expand=True, fill="both")
        
        header_label = tk.Label(main_frame, text=" ", font=("Arial", 30), bg=f"{self.rgb_to_hex(139,140,142)}")
        header_label.pack(pady=(0, 1))

        lfields = [
            ("counter", "Current Counter"),
            ("fcounter", "Future Counter"),
            ("distance", "Distance Crossed"),
        ]
        
        ldfields = [
            ("oil_type", "Oil Type"),
            ("oil_filter", "Oil Filter Type"),
            ("air_filter", "Air Filter Type"),
            ("diesel_filter", "Diesel Filter"),
        ]
        
        rfields = [
            ("gas_filter", "Gas Filter"),
            ("wipers", "Car Wipers"),
            ("front_break", "Front Break"),
            ("back_break", "Back Break"),
            ("timing_belt", "Timing Belt"),
            ("ac_filter", "AC Filter")
        ]
        rdfields = [
            ("coast", "Total Coast"),
            ("payed", "Amount Paid"),
            ("debit", "Debit"),
        ]

        left_frame = tk.Frame(main_frame, bg=self.rgb_to_hex(139,140,142))
        left_frame.pack(side="left", padx=10, anchor="n")

        right_frame = tk.Frame(main_frame, bg=self.rgb_to_hex(139,140,142))
        right_frame.pack(side="right", padx=10,  anchor="n")

        self.drop_vars={}
        entry_widgets = {}
        label = tk.Label(left_frame, text="Visit Date", font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.vd = DateEntry(left_frame)
        self.vd.set_date(datetime.now().date())
        self.drop_vars["date"]=self.vd
        self.vd.config(width=15)
        self.vd.grid(row=0, column=1,sticky="e", padx=5, pady=5)
        
        entry_widgets['date'] = self.vd
        
        label = tk.Label(left_frame, text="Next Chekup", font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        nxdate=self.nxt_date_chkup()
        self.nxt_chkup_var = tk.StringVar(left_frame)
        self.nxt_chkup = DateEntry(left_frame)
        self.nxt_chkup.set_date(nxdate.date())
        self.drop_vars["chkup"]=self.nxt_chkup_var
        self.nxt_chkup_var.trace_add("write", lambda *args, kind="chkup": self.kind_var_changed(kind, *args))
        self.nxt_chkup.config(width=15)
        self.nxt_chkup.grid(row=1, column=1,sticky="e", padx=5, pady=5)
        
        entry_widgets['chkup'] = self.nxt_chkup
        
        
        for i, (key, label_text) in enumerate(lfields):
            label = tk.Label(left_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i+2, column=0, sticky="w", padx=5, pady=5)

            entry = ttk.Entry(left_frame, width=15, font=("Arial", 10))
            entry.grid(row=i+2, column=1, padx=5, pady=5)
            entry_widgets[key] = entry
            entry_widgets[key].bind("<KeyRelease>", self.tacc)
            entry_widgets[key].bind("<Return>", lambda event, ew=entry_widgets[key]: self.next_entry(event, ew))
        
        for i, (key, label_text) in enumerate(ldfields):
            label = tk.Label(left_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i+5, column=0, sticky="w", padx=5, pady=5)

            kind_var = tk.StringVar(left_frame)
            kind_var.set(xx[key][0])  # Set the default value
            self.drop_vars[label_text]=kind_var
            kind_var.trace_add("write", lambda *args, kind=label_text: self.kind_var_changed(kind, *args))
            kind_menu = ttk.OptionMenu(left_frame , kind_var, xx[key][0], *xx[key]) 
            kind_menu.config(width=13)
            kind_menu.grid(row=i+5, column=1, sticky="e", padx=5, pady=5)
            entry_widgets[key] = kind_menu
            
        for i, (key, label_text) in enumerate(rfields):
            label = tk.Label(right_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            kind_var = tk.StringVar(right_frame)
            kind_var.set(xx[key][0])  # Set the default value
            self.drop_vars[label_text]=kind_var
            kind_var.trace_add("write", lambda *args, kind=label_text: self.kind_var_changed(kind, *args))

            kind_menu = ttk.OptionMenu(right_frame , kind_var, xx[key][0], *xx[key])
            kind_menu.config(width=13)
            kind_menu.grid(row=i, column=1, sticky="e", padx=5, pady=5)
            entry_widgets[key] = kind_menu
            
        for i, (key, label_text) in enumerate(rdfields):
            label = tk.Label(right_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i+6, column=0, sticky="w", padx=5, pady=5)

            entry = ttk.Entry(right_frame, width=15, font=("Arial", 10))
            entry.grid(row=i+6, column=1, padx=5, pady=5)
            entry_widgets[key] = entry
            entry_widgets[key].bind("<KeyRelease>", self.tacc)
            entry_widgets[key].bind("<Return>", lambda event, ew=entry_widgets[key]: self.next_entry(event, ew))

        dtls = tk.Frame(self.C_frame, bg=self.rgb_to_hex(139,140,142))  # New frame for buttons
        dtls.pack()

        entrydetails = tk.Text(dtls, width=80, font=("Arial", 10))
        entrydetails.grid(row=0, column=0, padx=5)
        entrydetails.configure(height=6)
        entry_widgets['details'] = entrydetails
        

        ctrs = tk.Frame(self.C_frame, bg=self.rgb_to_hex(139,140,142))
        ctrs.pack(pady=10)

        button_frame = tk.Frame(ctrs, bg=self.rgb_to_hex(139,140,142))
        button_frame.grid(row=0, column=0)

        button = tk.Button(button_frame, text="car folder", font=("Arial", 10), command=self.open_file)
        button.grid(row=0, column=0, padx=5, pady=5)

        buttonp = tk.Button(button_frame, text= "prev", font=("Arial", 10), width=5 ,command=self.pervv)
        buttonp.grid(row=0, column=1, padx=5, pady=5)

        buttonn = tk.Button(button_frame, text= "next", font=("Arial", 10), width=5,command=self.nextt)
        buttonn.grid(row=0, column=2, padx=5, pady=5)

        buttonf = tk.Button(button_frame, text="first", font=("Arial", 10), width=5,command=self.first)
        buttonf.grid(row=0, column=3, padx=5, pady=5)

        buttonll = tk.Button(button_frame, text="last", font=("Arial", 10), width=5,command=self.last)
        buttonll.grid(row=0, column=4, padx=5, pady=5)

        buttonnow = tk.Label(button_frame, text='            ', font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        buttonnow.grid(row=0, column=5, padx=5, pady=5)

        b_frame = tk.Frame(ctrs, bg=f"{self.rgb_to_hex(139,140,142)}")  # New frame for buttons
        b_frame.grid(row=0, column=1)

        button = tk.Button(b_frame, text="search", font=("Arial", 10), width=5,command=self.search)
        button.grid(row=1, column=1, padx=5, pady=5)

        self.sc = ttk.Entry(b_frame,width=15, font=("Arial", 10))
        self.sc.grid(row=1, column=2, padx=5, pady=5)
        entry_widgets["search"] = self.sc
        entry_widgets["search"].insert(0, f"{datetime.now().date()}")
        

        self.entry_widgets = entry_widgets
        return self.C_frame
        
    def toggle_date_entries(self):
        if self.show_date_checkbox_var.get() and self.show_v_checkbox_var.get():
            self.result_frame.pack_forget()
            self.search_button.pack_forget()
            self.dropp_frame.pack_forget()
            self.se_frame.pack_forget()
            self.se_frame.pack()
            self.dropp_frame.pack(pady=5)
            self.result_frame.pack(pady=10)# Move button to the bottom
            self.search_button.pack(padx=(55,0),pady=15)
        elif self.show_date_checkbox_var.get():
            self.result_frame.pack_forget()
            self.search_button.pack_forget()
            self.dropp_frame.pack_forget()
            self.se_frame.pack(pady=5)
            self.result_frame.pack(pady=5)# Move button to the bottom
            self.search_button.pack(padx=(55,0),pady=15) 
        elif self.show_v_checkbox_var.get():
            self.result_frame.pack_forget()
            self.search_button.pack_forget()
            self.se_frame.pack_forget()
            self.dropp_frame.pack(pady=5)
            self.result_frame.pack(pady=10)# Move button to the bottom
            self.search_button.pack(padx=(55,0),pady=15) 
        else:
            self.result_frame.pack_forget()
            self.search_button.pack_forget()
            self.dropp_frame.pack_forget()
            self.se_frame.pack_forget()
            self.result_frame.pack(pady=10)# Reset button position
            self.search_button.pack(padx=(55,0),pady=15) 

    def ssearch(self):
        start_date = self.start_date_entry.get_date().isoformat()
        end_date = self.end_date_entry.get_date().isoformat()
        details = self.details_entry.get()

        # Connect to the database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Construct the base query
        query = "SELECT COUNT(DISTINCT lplate), SUM(debit), SUM(payed) FROM visits"

        # Construct the WHERE clause based on the input

        # Initialize the params list
        params = []
        conditions = []

        if self.show_date_checkbox_var.get():
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
        if details:
            conditions.append("details LIKE ?")
            params.append(f'%{details}%')
            
         
        if self.show_v_checkbox_var.get():
            # Add chkup condition if it's not the default date
            if  "2000-01-01" in self.nxt_chkup_var.get():
                conditions.append("chkup = ?")
                params.append(self.nxt_chkup_var.get())

            # Add conditions for non-blank and "No Change" stat_widgets
            for key, var in self.dropp_vars.items():
                if not key in ['date','chkup']:
                    value = var.get()
                    if value not in ["", "No Change"]:
                        conditions.append(f"{key} = ?")
                        params.append(value)
                    
        # Add conditions to the query if any are present
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query with parameters
        cursor.execute(query, params)
        result = cursor.fetchone()

        if conditions:
            query +=" AND debit > 0"
        else:
            query += " WHERE debit > 0"
        cursor.execute(query, params)
        unpaid_customers_result = cursor.fetchone()
        
        total_customers = result[0]
        total_debit = result[1] if result[1] else 0
        total_payed = result[2] if result[2] else 0

        unpaid_customers = unpaid_customers_result[0] if unpaid_customers_result else 0

        self.total_customers_text.delete(0, tk.END)
        self.total_customers_text.insert(0, str(total_customers))

        self.unpaid_customers_text.delete(0, tk.END)
        self.unpaid_customers_text.insert(0, str(unpaid_customers))

        self.total_debit_text.delete(0, tk.END)
        self.total_debit_text.insert(0, str(total_debit))

        self.total_payed_text.delete(0, tk.END)
        self.total_payed_text.insert(0, str(total_payed))

        # Close the connection
        conn.close()

    def create_settings_page(self, parent,user_data):
        self.root.configure(bg=f"{self.rgb_to_hex(139,140,142)}") 
        self.mm_frame = tk.Frame(parent, bg=f"{self.rgb_to_hex(139,140,142)}")
        self.topp_frame = tk.Frame(self.mm_frame, bg=self.rgb_to_hex(139,140,142))
        self.details_label = tk.Label(self.topp_frame, text="Visit Details:", bg=f"{self.rgb_to_hex(139,140,142)}", font=("Arial", 15)) 
        self.details_label.grid(row=0, column=0, padx=(15,5), pady=5)
        self.details_entry = ttk.Entry(self.topp_frame)
        self.details_entry.grid(row=0, column=1, padx=5, pady=5)
        self.topp_frame.pack()

        self.show_date_checkbox_var = tk.BooleanVar()
        self.show_date_checkbox = tk.Checkbutton(self.topp_frame, text="Search by Date", variable=self.show_date_checkbox_var, font=("Arial", 13), command=self.toggle_date_entries, bg=f"{self.rgb_to_hex(139,140,142)}")
        self.show_date_checkbox.grid(row=0, column=2, padx=5,pady=5)
        
        self.show_v_checkbox_var = tk.BooleanVar()
        self.show_v_checkbox = tk.Checkbutton(self.topp_frame, text="Search by Visit Details", variable=self.show_v_checkbox_var, font=("Arial", 13), command=self.toggle_date_entries, bg=f"{self.rgb_to_hex(139,140,142)}")
        self.show_v_checkbox.grid(row=0, column=3, padx=5,pady=20)
        
        self.se_frame = tk.Frame(self.mm_frame, bg=self.rgb_to_hex(139,140,142))
        
        leftl_frame = tk.Frame(self.se_frame, bg=self.rgb_to_hex(139,140,142))
        leftl_frame.pack(side="left", padx=15, anchor="n")

        rightr_frame = tk.Frame(self.se_frame, bg=self.rgb_to_hex(139,140,142))
        rightr_frame.pack(side="right", padx=15,  anchor="n")
        
        self.start_date_label = tk.Label(leftl_frame, text="Start Date:", bg=f"{self.rgb_to_hex(139,140,142)}", font=("Arial", 15))
        self.start_date_label.grid(row=0, column=0,sticky="w", padx=(10,28), pady=5)
        self.start_date_entry = DateEntry(leftl_frame)
        self.start_date_entry.config(width=15)
        self.start_date_entry.grid(row=0, column=1,sticky="e", padx=(10,0), pady=5)
        
        self.end_date_label = tk.Label(rightr_frame, text="End Date:", bg=f"{self.rgb_to_hex(139,140,142)}", font=("Arial", 15))
        self.end_date_label.grid(row=0, column=0, sticky="w", padx=(0,15), pady=5)
        self.end_date_entry = DateEntry(rightr_frame)
        self.end_date_entry.config(width=15)
        self.end_date_entry.grid(row=0, column=1,sticky="e", padx=10, pady=5)
        
        
        self.dropp_frame = tk.Frame(self.mm_frame, bg=self.rgb_to_hex(139,140,142))
        xx={}
        xp={}
        for k in self.ki:
            xx[k]=[l["name"] for l in self.ki[k]]
            xp[k]=[l["price"] for l in self.ki[k]]
        self.xx=xx
        self.xp=xp 
        
        ldfields = [
            ("oil_type", "Oil Type"),
            ("oil_filter", "Oil Filter Type"),
            ("air_filter", "Air Filter Type"),
            ("diesel_filter", "Diesel Filter"),
            ("gas_filter", "Gas Filter"),
        ]
        
        rfields = [
            ("wipers", "Car Wipers"),
            ("front_break", "Front Break"),
            ("back_break", "Back Break"),
            ("timing_belt", "Timing Belt"),
            ("ac_filter", "AC Filter"),
        ]

        left_frame = tk.Frame(self.dropp_frame, bg=self.rgb_to_hex(139,140,142))
        left_frame.pack(side="left", padx=10, anchor="n")

        right_frame = tk.Frame(self.dropp_frame, bg=self.rgb_to_hex(139,140,142))
        right_frame.pack(side="right", padx=10,  anchor="n")

        self.dropp_vars={}
        entry_widgets = {}
        
        nxdate=date(2000, 1, 1)
        label = tk.Label(left_frame, text="Next Chekup", font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.nxt_chkup_var = tk.StringVar(left_frame)
        self.nxt_chkup = DateEntry(left_frame)
        self.nxt_chkup.set_date(nxdate)
        self.dropp_vars["chkup"]=self.nxt_chkup_var
        self.nxt_chkup.config(width=15)
        self.nxt_chkup.grid(row=1, column=1,sticky="e", padx=5, pady=5)
        
        entry_widgets['chkup'] = self.nxt_chkup
        
        for i, (key, label_text) in enumerate(ldfields):
            label = tk.Label(left_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i+2, column=0, sticky="w", padx=5, pady=5)

            kind_var = tk.StringVar(left_frame)
            kind_var.set(xx[key][0])  # Set the default value
            self.dropp_vars[self.fss[label_text]]=kind_var
            kind_menu = ttk.OptionMenu(left_frame , kind_var,  xx[key][0], *xx[key]) 
            kind_menu.config(width=13)
            kind_menu.grid(row=i+2, column=1, sticky="e", padx=5, pady=5)
            entry_widgets[key] = kind_menu
            
        for i, (key, label_text) in enumerate(rfields):
            label = tk.Label(right_frame, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            kind_var = tk.StringVar(right_frame)
            kind_var.set(xx[key][0])  # Set the default value
            self.dropp_vars[self.fss[label_text]]=kind_var

            kind_menu = ttk.OptionMenu(right_frame , kind_var,  xx[key][0], *xx[key])
            kind_menu.config(width=13)
            kind_menu.grid(row=i, column=1, sticky="e", padx=5, pady=5)
            entry_widgets[key] = kind_menu
         
        self.stat_widgets = entry_widgets
        
        self.search_button = tk.Button(self.mm_frame, text="Search",width=15 ,command=self.ssearch )

        #self.result_label = tk.Label(self.mm_frame, text="", bg=f"{self.rgb_to_hex(139,140,142)}", font=("Arial", 10))
        self.result_frame = tk.Frame(self.mm_frame, bg=self.rgb_to_hex(139,140,142))

        # Create labels and text boxes for displaying the results
        total_customers_label = tk.Label(self.result_frame, text="Total Customers:", bg=self.rgb_to_hex(139,140,142), font=("Arial", 15))
        total_customers_label.grid(row=0, column=0,sticky="w", padx=5, pady=5)
        self.total_customers_text = ttk.Entry(self.result_frame,width=20 , font=("Arial", 10))
        self.total_customers_text.grid(row=0, column=1,sticky="e", padx=5, pady=5)

        unpaid_customers_label = tk.Label(self.result_frame, text="Customers With Debit:", bg=self.rgb_to_hex(139,140,142), font=("Arial", 15))
        unpaid_customers_label.grid(row=0, column=2,sticky="w", padx=5, pady=5)
        self.unpaid_customers_text = ttk.Entry(self.result_frame,width=20 , font=("Arial", 10))
        self.unpaid_customers_text.grid(row=0, column=3,sticky="e", padx=5, pady=5)

        total_debit_label = tk.Label(self.result_frame, text="Total Debit:", bg=self.rgb_to_hex(139,140,142), font=("Arial", 15))
        total_debit_label.grid(row=1, column=0,sticky="w", padx=5, pady=5)
        self.total_debit_text = ttk.Entry(self.result_frame, width=20 ,font=("Arial", 10))
        self.total_debit_text.grid(row=1, column=1,sticky="e", padx=5, pady=5)

        total_payed_label = tk.Label(self.result_frame, text="Total Revenue:", bg=self.rgb_to_hex(139,140,142), font=("Arial", 15))
        total_payed_label.grid(row=1, column=2,sticky="w", padx=5, pady=5)
        self.total_payed_text = ttk.Entry(self.result_frame,width=20 , font=("Arial", 10))
        self.total_payed_text.grid(row=1, column=3,sticky="e", padx=5, pady=5)
        
        # Position the Search button under the checkbox initially
        self.result_frame.pack(pady=10)
        self.search_button.pack(padx=(55,0),pady=15)
        return self.mm_frame

    def tacc(self,event):
        # Get the widget that triggered the event
        entry_widget = event.widget
        if self.modo in ['v']:
            # Get the widget's key (e.g., "name", "id No.", etc.)
            key = next((k for k, v in self.entry_widgets.items() if v == entry_widget), None)
            if key:
                # Update the data in MongoDB based on the key and the new value in the Entry widget
                no = self.current_value
                nn = self.visits
                if len(nn) < no:
                    nn={
                    "vno":no,
                    "date": self.vd.get_date().isoformat(),
                    "chkup": self.nxt_chkup.get_date().isoformat(),
                    "counter": 0,
                    "fcounter": 0,
                    "distance": 0,
                    "oil_type": 'No Change',
                    "oil_filter": 'No Change',
                    "air_filter": 'No Change',
                    "diesel_filter": 'No Change',
                    "ac_filter": 'No Change',
                    "gas_filter": 'No Change',
                    "wipers": 'No Change',
                    "front_break": 'No Change',
                    "back_break": 'No Change',
                    "timing_belt": 'No Change',
                    "coast": 0,
                    "payed": 0,
                    "debit":0,
                    'details':'',
                    "lplate": self.plate,
                }
                else:
                    nn=nn[no-1]

                if key in["details"]:
                    nn[key]=entry_widget.get("1.0",tk.END)
                    self.insert_or_update_data_to_visits(nn)
                elif key in ["search"]:
                    pass
                elif key in["payed"]:
                    nn[key] = entry_widget.get().strip()
                    self.payed_var_changed()
                    self.insert_or_update_data_to_visits(nn)
                else:
                    nn[key] = entry_widget.get().strip()
                    self.insert_or_update_data_to_visits(nn)
        elif self.modo in ['k']:
            key = next((k for k, v in self.entry_widgets.items() if v == entry_widget), None)

            if key:
                # Update the data in MongoDB based on the key and the new value in the Entry widget
                no = self.current_value
                nn = self.get_all_visits_for_car(self.plate)
                if len(nn)-1 > no:
                    nn={
                    "vno":no,
                    "date": self.vd.get_date().isoformat(),
                    "chkup": self.nxt_chkup.get_date().isoformat(),
                    "counter": 0,
                    "fcounter": 0,
                    "distance": 0,
                    "oil_type": 'No Change',
                    "oil_filter": 'No Change',
                    "air_filter": 'No Change',
                    "diesel_filter": 'No Change',
                    "ac_filter": 'No Change',
                    "gas_filter": 'No Change',
                    "wipers": 'No Change',
                    "front_break": 'No Change',
                    "back_break": 'No Change',
                    "timing_belt": 'No Change',
                    "coast": 0,
                    "payed": 0,
                    "debit":0,
                    'details':'',
                    "lplate": self.plate,
                }
                else:
                    nn=nn[no-1]
            
                if key in["details"]:
                    nn[key]=entry_widget.get("1.0",tk.END)
                    self.insert_or_update_data_to_visits(nn)
                elif key in ["search"]:
                    pass
                else:
                    nn[key] = entry_widget.get().strip()
                    self.insert_or_update_data_to_visits(nn)
        
    def get_allskinds_kind(self,name):
        c=self.get_skinds_by_no(self.get_kinds_by_name(name)["kno"])
        return c
    
    def ccf(self,namee):
        self.car_folder_path=self.create_car_folder(namee)
    
    def nxt_date_chkup(self):
        current_date = datetime.now()
        six_months_from_now = current_date + timedelta(days=30 * 6)
    
        return six_months_from_now
    
    def create_editkinds_page(self,parent,user_data):
        self.mkframe= tk.Frame(parent, bg=self.rgb_to_hex(139,140,142))
        
        options = ["choose to edit"]
        for i in self.fmore:#[j['name'] for j in self.ki[i]]
            options.append( self.fless[i])
        self.edittype_var = tk.StringVar(self.mkframe)
        self.edittype_var.set(options[0])  # Set the default value
        self.edittype_var.trace_add("write", self.edittype_var_changed)
         
        type_menu = ttk.OptionMenu(self.mkframe, self.edittype_var, *options)
        type_menu.config(width=18)
        type_menu.pack( pady=5)
        self.content_frame = None  # To store the content frame
        
        return self.mkframe
    
    def edittype_var_changed(self, *args):
        selected_option = self.edittype_var.get()
        if selected_option != "choose to edit":
            selected_option = self.fss[selected_option]
            ki=self.ki[selected_option]
            if self.content_frame:
                self.content_frame.destroy()  # Destroy the existing content frame if it exists
            self.content_frame = self.create_editkinds_scroll([j['name'] for j in ki], [j['price'] for j in ki],self.mkframe)
            self.content_frame.pack( pady=15)
    
    def create_editkinds_scroll(self, lstt, prices, parent):
        mframe= tk.Frame(parent, bg=self.rgb_to_hex(139,140,142))
        main_frame = tk.Frame(mframe, bg=self.rgb_to_hex(139,140,142))
        main_frame.pack(expand=True, fill="both")
        label = tk.Label(main_frame, text='Product', font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        label.grid(row=0,sticky="w", column=1, padx=40, pady=5)
        entry = tk.Label(main_frame, text='Price', font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
        entry.grid(row=0,sticky="e", column=2, padx=25, pady=5)  
        lfb=tk.Frame(mframe,bg=self.rgb_to_hex(139,140,142))
        lfb.pack(padx=15)
        self.fcanvas = tk.Canvas(lfb)
        self.fcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ffframe = tk.Frame(self.fcanvas)
        self.ffframe.pack(expand=True, fill="both")
        
        bcb = tk.Button(lfb, text='+', command=self.add_kind, font=("Arial", 15),)# bg=self.rgb_to_hex(100, 190, 100))
        bcb.pack(side='right',padx=3)
        scrollbar = ttk.Scrollbar(lfb, orient=tk.VERTICAL, command=self.fcanvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fcanvas.configure(yscrollcommand=scrollbar.set)

        
        # Calculate the position to center the frame in the canvas
        x0 = self.ffframe.winfo_screenwidth()/2
        y0 = self.ffframe.winfo_screenheight()/2
        self.fcanvas.create_window((x0-440,y0+455), window=self.ffframe, anchor = "center")
        
        self.fcanvas.bind("<Configure>", self.configure_canvas)
        self.fcanvas.bind("<MouseWheel>", self.on_mousewheel)
        self.ffframe.bind("<MouseWheel>", self.on_mousewheel)

        lfields = lstt
        price = {}
        text_vars = {}
        ptext_vars = {}

        self.isadded = False
        for i in range(len(lfields)):
            label_text = lfields[i]
            key = f'{i}'
            text_var = tk.StringVar()
            text_var.set(label_text)
            text_vars[key] = text_var
            price[key] = str(prices[i])
            ptext_var = tk.StringVar()
            ptext_var.set(price[key])
            ptext_vars[key] = ptext_var

            entry = tk.Entry(self.ffframe, width=15, font=("Arial", 10), textvariable=text_var)
            entry.grid(row=i, column=0, padx=5, pady=5)
            entry.bind("<MouseWheel>", self.on_mousewheel)
            entry.bind("<KeyRelease>", lambda event, key=i, field='name', text_var=text_var: self.update_ki( key, field, text_var))

            entry = tk.Entry(self.ffframe, width=15, font=("Arial", 10), textvariable=ptext_var)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.bind("<MouseWheel>", self.on_mousewheel)
            entry.bind("<KeyRelease>", lambda event, key=i, field='price', text_var=ptext_var: self.update_ki( key, field, text_var))
            # Update self.ki when the entry is changed

            if i in [0, 1] and self.edittype_var.get() not in ['l']:
                pass
            else:
                bb = tk.Button(self.ffframe, text='-', height=1, command=lambda kindno=i: self.del_kind(kindno),
                               font=("Arial", 10), bg=self.rgb_to_hex(190, 100, 100))
                bb.grid(row=i, column=2, padx=5, pady=2)
                bb.bind("<MouseWheel>", self.on_mousewheel)

        savbtn = tk.Button(mframe, text="Save", width=10, command=self.savv)
        savbtn.pack(pady=5)

        self.lasteditno = i
        return mframe

    def create_srch_page(self, parent, user_data):
        self.srch_frame = tk.Frame(parent, bg=self.rgb_to_hex(139, 140, 142))

        # Search by ID Section
        id_frame = tk.Frame(self.srch_frame, bg=self.rgb_to_hex(139, 140, 142))
        id_frame.pack(pady=20,padx=20)

        id_entry = ttk.Entry(id_frame, font=("Arial", 13))
        id_entry.grid(row=0, column=0, padx=(15,5), pady=5)

        id_search_btn = ttk.Button(id_frame, text="Search by Id Number", command=lambda: self.srch_by_id(id_entry.get()))
        id_search_btn.grid(row=0, column=1, padx=(15,5), pady=5)

        plate_search_btn = ttk.Button(id_frame, text="Search by Plate Number", command=lambda: self.srch_by_plate(id_entry.get()))
        plate_search_btn.grid(row=0, column=2, padx=(15,5), pady=5)
        
        self.srchmain=None

        return self.srch_frame

    def srch_by_id(self, user_id):
        # Your logic for searching by ID here
        if self.srchmain:
            self.srchmain.destroy()  # Destroy the existing content frame if it exists
        cars=self.get_all_c2i(user_id)
        if cars == 'non':
            self.srchmain = tk.Label(self.srch_frame, text='The id is not registered', font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            self.srchmain.pack( pady=15)
        else:
            plates=[]
            payed=[]
            debit=[]
            for i in cars:
                plates.append(i['plate'])
                payed.append(i['payed'])
                debit.append(i['debit'])
            self.srchmain = self.create_srch_scroll(plates,payed,debit,self.srch_frame)
            self.srchmain.pack( pady=15)

    def srch_by_plate(self, plate_number):
        if self.srchmain:
            self.srchmain.destroy()
        self.get_c2srch(plate_number)
    
    def get_c2srch(self,plate):
        car=self.get_car_by_no(plate)
        if car:
            self.srchmain = tk.Frame(self.srch_frame, bg=self.rgb_to_hex(139, 140, 142))
            lfields = [
                    (car["model"], "Car Model"),
                    (car["payed"], "Paid"),
                    (car["debit"], "Debit"),
                    (car["email"],"Email"),
                    (car["phone"],"Phone Number"),
                    (car["idNo"],"Id Number"),
                ]
            
            for i, (val, label_text) in enumerate(lfields):
                
                label = tk.Label(self.srchmain, text=label_text, font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
                label.grid(row=i,sticky="w", column=0, padx=5, pady=5)

                entry = ttk.Entry(self.srchmain, width=20, font=("Arial", 10))
                entry.grid(row=i, column=1, padx=5, pady=5)
                entry.insert(0, str(val))

            self.srchmain.pack( pady=15) 
        else:
            self.srchmain = tk.Label(self.srch_frame, text='The car is not registered', font=("Arial", 15), bg=self.rgb_to_hex(139,140,142))
            self.srchmain.pack( pady=15)
    
    def create_srch_scroll(self, plates, payed,debit, parent):
        mframe= tk.Frame(parent, bg=self.rgb_to_hex(139,140,142))
         
        lfb=tk.Frame(mframe)
        lfb.pack(padx=0)
        self.srchcanvas = tk.Canvas(lfb)
        self.srchcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.srchrame = tk.Frame(self.srchcanvas)
        self.srchrame.pack(expand=True, fill="both")
        
        # Calculate the position to center the frame in the canvas
        x0 = self.srchrame.winfo_screenwidth()/2
        y0 = self.srchrame.winfo_screenheight()/2
        self.srchcanvas.create_window((x0-440,y0+455), window=self.srchrame, anchor = "center")
        
        self.srchcanvas.bind("<Configure>", self.configure_anvas)
        self.srchcanvas.bind("<MouseWheel>", self.onmousewheel)
        self.srchrame.bind("<MouseWheel>", self.onmousewheel)

        lfields = plates
        price = {}
        text_vars = {}
        ptext_vars = {}

        self.isadded = False
        
        a = tk.Label(self.srchrame,width=15, text='Car Number', font=("Arial", 15))
        a.grid(row=0, column=0, padx=5, pady=5)
        
        b = tk.Label(self.srchrame,width=15, text='Paid', font=("Arial", 15))
        b.grid(row=0, column=1, padx=5, pady=5)
        
        c = tk.Label(self.srchrame,width=15, text='Debit', font=("Arial", 15))
        c.grid(row=0, column=2, padx=5, pady=5)
        
        for i in range(len(lfields)):
            label_text = lfields[i]
            key = f'{i}'
            text_var = tk.StringVar()
            text_var.set(label_text)
            
            ptext_var = tk.StringVar()
            ptext_var.set(payed[i])
            
            debittext_var = tk.StringVar()
            debittext_var.set(debit[i])
            
            entry = tk.Entry(self.srchrame, width=15, font=("Arial", 10), textvariable=text_var)
            entry.grid(row=i+1, column=0, padx=5, pady=5)
            entry.bind("<MouseWheel>", self.onmousewheel)

            entry = tk.Entry(self.srchrame, width=15, font=("Arial", 10), textvariable=ptext_var)
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            entry.bind("<MouseWheel>", self.onmousewheel)
            
            entry = tk.Entry(self.srchrame, width=15, font=("Arial", 10), textvariable=debittext_var)
            entry.grid(row=i+1, column=2, padx=5, pady=5)
            entry.bind("<MouseWheel>", self.onmousewheel)
            
        return mframe
  
    def get_all_c2i(self,idno):
        self.create_connection()
        query = "SELECT * FROM owners WHERE idNo = ?"
        result = self.fetch_data(query, (idno,))
        if result: 
            update_query = "SELECT * FROM cars WHERE idNo = ?"
            datas = self.fetch_data(update_query, (idno,))
            i=[]
            for data in datas:
                c={
                    "plate": data[1],
                    "payed": data[6], 
                    "debit": data[7]
                }
                i.append(c)
            return i
        else:
            return 'non'
  
    def update_ki(self,row, field, value):
        selected_option = self.edittype_var.get()
        selected_option = self.fss[selected_option]
        # Update the corresponding value in self.ki
        pro=value.get()
        if field == 'name':
            self.ki[selected_option][row]['name'] = pro
        elif field == 'price':
            if pro not in [''] and pro.isdigit():
                self.ki[selected_option][row]['price'] = float(pro)
            else:
                self.ki[selected_option][row]['price'] = 0 

    def dell_db(self,data):
        conn = self.create_connection()
        cursor = conn.cursor()
        sno=0
        sno=data['sno']
        conn = self.create_connection()
        query = "DELETE FROM skinds WHERE sno = ?"
        self.execute_query(conn, query, (sno,))
        conn.close()

    def del_kind(self,kindno):
        selected_option = self.edittype_var.get()
            
        ki=self.ki[self.fss[selected_option]]
        prices=[j['price'] for j in ki]
        names=[j['name'] for j in ki]
        for i in range(len(self.ki[self.fss[selected_option]])):
            if names[kindno]==self.ki[self.fss[selected_option]][i]['name']:
                del self.ki[self.fss[selected_option]][i]
                break
        del names[kindno]
        del prices[kindno]
        if selected_option != "choose to edit":
            if self.content_frame:
                self.content_frame.destroy()  # Destroy the existing content frame if it exists
            self.content_frame = self.create_editkinds_scroll(names,prices,self.mkframe)
            self.content_frame.pack( pady=15)
        
    def configure_canvas(self,event):
        self.fcanvas.configure(scrollregion=self.fcanvas.bbox("all"))
        self.fcanvas.config(width=self.ffframe.winfo_reqwidth(), height=self.ffframe.winfo_reqheight())
        
    def configure_anvas(self,event):
        self.srchcanvas.configure(scrollregion=self.srchcanvas.bbox("all"))
        self.srchcanvas.config(width=self.srchrame.winfo_reqwidth(), height=self.srchrame.winfo_reqheight())
        
    def on_mousewheel(self,event):
        self.fcanvas.yview_scroll(-1 * (event.delta // 30), "units")
        
    def onmousewheel(self,event):
        self.srchcanvas.yview_scroll(-1 * (event.delta // 30), "units")

    def add_kind(self):
        selected_option = self.edittype_var.get()
        kno=0
        for i in self.fless:
            kno+=1
            if self.fless[i] == selected_option:
                break
                
        ki=self.ki[self.fss[selected_option]]
        prices=[j['price'] for j in ki]
        names=[j['name'] for j in ki]
        c=len(self.ki[self.fss[selected_option]])
        self.ki[self.fss[selected_option]].append({'name': '', 'price': 0, 'kno': kno})
        names.append('')
        prices.append(0)
        if selected_option != "choose to edit":
            if self.content_frame:
                self.content_frame.destroy()  # Destroy the existing content frame if it exists
            self.content_frame = self.create_editkinds_scroll(names,prices ,self.mkframe)
            self.content_frame.pack( pady=15)   
    
    def savv(self):
        for i in self.ki:
            for j in self.ki[i] :
                if not j in self.si[i]:
                    self.insert_or_update_data_to_skinds(j)
                
        for i in self.si:
            for j in self.si[i] :
                if not j in self.ki[i]:
                    self.dell_db(j)
                    
        for k in self.fless:
            self.si[k]=self.get_allskinds_kind(k)
 
    def payed_var_changed(self):
        if 'debit' in self.entry_widgets:
            co=self.entry_widgets['coast'].get()
            payed=self.entry_widgets['payed'].get()
            di=self.entry_widgets['debit'].get()
            if co in ["",' ']:
                co=0
            else:
                co = float(co)
            if payed in ["",' ']:
                payed=0
            else:
                payed = float(payed)
            if di in ["",' ']:
                di=0
            else:
                di = float(di)
            ogp =co-payed
            if ogp>0:
                di=ogp
            else:
                di=0
            self.entry_widgets['debit'].delete(0, tk.END)
            self.entry_widgets['debit'].insert(0, str(di))
            no = self.current_value
            nn = self.visits
            if no-1>0:
                vn=nn[no-1]
            else:
                vn=nn[0]
            vn['debit'] += ogp
            self.insert_or_update_data_to_visits(vn)
        else:
            pass
        
    def get_visit_by_no(self,vno,lplate):
        query = "SELECT * FROM visits WHERE vno = ? AND lplate = ?"
        data = self.fetch_data(query, (vno,lplate,))
        if data:
            i={
                "avno":data[0][0],
                "vno": data[0][1],
                "date": data[0][2],             
                "chkup": data[0][3],
                "counter": data[0][4],
                "fcounter": data[0][5],
                "distance": data[0][6],
                "oil_type": data[0][7],
                "oil_filter": data[0][8],
                "air_filter": data[0][9],              
                "diesel_filter": data[0][10],             
                "ac_filter": data[0][11], 
                "gas_filter": data[0][12],
                "wipers" : data[0][13] ,      
                "front_break": data[0][14],   
                "back_break": data[0][15],      
                "timing_belt": data[0][16],       
                "coast":data[0][17],       
                "payed": data[0][18],  
                "debit": data[0][19], 
                "details": data[0][20],   
                "lplate": lplate  
            }
            return i
        else:
            return None
 
    def execute_query(self,conn, query, data=None):
        cur = conn.cursor()
        if data:
            cur.execute(query, data)
            conn.commit()
        else:
            cur.execute(query)
            conn.commit()
        return cur.lastrowid

    def insert_or_update_data_to_owners(self,data):
        conn=self.create_connection()
        query = "SELECT * FROM owners WHERE idNo = ?"
        result = self.fetch_data(query, (data["idNo"],))
        if result: 
            update_query = "UPDATE owners SET name = ?,phone = ?,email = ? WHERE idNo = ?"
            self.execute_query(conn, update_query, (data['name'],data['phone'],data['email'],data['idNo']))
        else:
            insert_query = f"INSERT INTO owners (idNo,name,phone,email) VALUES (?, ?, ?, ?)"
            self.execute_query(conn, insert_query, (data['idNo'],data['name'],data['phone'],data['email']))
        
    def insert_or_update_data_to_cars(self,data):
        conn=self.create_connection()
        query = "SELECT * FROM cars WHERE lplate = ?"
        result = self.fetch_data(query, (data["lplate"],))
        if result: 
            update_query = "UPDATE cars SET model = ?,phone = ?,email = ?,gastyp = ?,payed = ?,debit = ?,cfno = ?,lvno = ? WHERE lplate = ?"
            self.execute_query(conn, update_query, (data['model'],data['phone'],data['email'],data['gastyp'],data['payed'],data['debit'],
                                                    data['lvno'],data['lplate']))
        else:
            insert_query = f"INSERT INTO cars (lplate,model,phone,email,gastyp,payed,debit,lvno,idNo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            self.execute_query(conn, insert_query, (data['lplate'],data['model'],data['phone'],data['email'],data['gastyp'],
                                                    data['payed'],data['debit'],data['lvno'],data['idNo']))

    def insert_or_update_data_to_visits(self,data):
        conn=self.create_connection()
        if 'vno' in data:
            lvno=data['vno']-1
        elif self.current_value-1 > 0:
            lvno=self.current_value-1
        else:
            lvno=0
        self.update_current_value(lvno+1)
        query = "SELECT * FROM visits WHERE date = ?"
        result = self.fetch_data(query, (data["date"],))
        if result: 
            if 'details' in data:
                details_value = data['details']
            else:
                details_value = "" 
            update_query = """UPDATE visits SET chkup = ?,counter = ?,fcounter = ?,distance = ?,oil_type = ?,oil_filter = ?,air_filter = ?,diesel_filter = ?,ac_filter = ?,gas_filter = ?,wipers = ?,front_break = ?,back_break = ?,timing_belt = ?,coast = ?,payed = ?,debit = ?,details = ?,lplate = ? WHERE date = ?"""
            self.execute_query(conn, update_query, (data['chkup'],data['counter'],data['fcounter'],data['distance'],data['oil_type'],data['oil_filter'],
                                           data['air_filter'],data['diesel_filter'],data['ac_filter'],data['gas_filter'],data['wipers'],data['front_break'],
                                           data['back_break'],data['timing_belt'],data['coast'],data['payed'],data['debit'],details_value,data['lplate'],data['date']))
        else:
            insert_query =f"INSERT INTO visits (vno, date, chkup, counter, fcounter, distance, oil_type, oil_filter, air_filter, diesel_filter, ac_filter, gas_filter, wipers, front_break, back_break, timing_belt, coast, payed, debit, details, lplate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            self.execute_query(conn, insert_query, (lvno+1, data['date'], data['chkup'], data['counter'], data['fcounter'],
                                            data['distance'], data['oil_type'], data['oil_filter'], data['air_filter'],
                                            data['diesel_filter'], data['ac_filter'], data['gas_filter'], data['wipers'],
                                            data['front_break'], data['back_break'], data['timing_belt'], data['coast'],
                                            data['payed'], data['debit'], data['details'], data['lplate']))
            
            self.set_lvno(lvno+2)
            self.create_date_folder(data['date'])
        self.visits=self.get_all_visits_for_car(self.plate)
    
    def set_lvno(self,no):
        conn=self.create_connection()
        update_query = "UPDATE cars SET lvno = ? WHERE lplate = ?"
        self.execute_query(conn, update_query, (no,self.plate))



if __name__ == "__main__":
    app = MainClass()
    app.root.mainloop()
