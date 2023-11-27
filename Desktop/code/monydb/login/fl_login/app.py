import os
import shutil
import pathlib
import json
import requests
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from flask import Flask, session, abort, redirect, request,render_template, jsonify
from flask_cors import CORS
from google.oauth2 import id_token
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import webbrowser
import firebase_admin
from firebase_admin import credentials, db
import paypalrestsdk
from paypalrestsdk import Payment
import secrets
import uuid
import string

appname='Binder'
cname='RiaSoftware'
app = Flask(f"{cname} {appname} App")
CORS(app)
app.secret_key = "abcdefghijk123"
appurl='http://127.0.0.1:5000'
basicprice=180
premprice=240
global bPay 
bPay =False
global prePay
prePay= False
global password
password = "@Ksoftkhaafif1"  # Change this to your secure password


# Initialize Firebase with your Firebase project's credentials
cred = credentials.Certificate(r"C:\Users\khaaf\Desktop\code\monydb\login\fl_login\key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monydb-f2cdb-default-rtdb.europe-west1.firebasedatabase.app/'
})
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "107932074863-nlil9n5j9lmahqfb15cmn52u59evpse9.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret1.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=f"{appurl}/callback"
)

def create_fernet():
        global password
        # Derive a key from the password using PBKDF2HMAC
        password = password.encode()
        salt = b"MY_Potatolikesme_too"  # Change this to a unique salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=100000,  # Adjust the number of iterations as needed
            salt=salt,
            length=32  # The length of the derived key
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))

        return Fernet(key)

def encrypt_data(data):
        return fernet.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data):
        try:
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        except InvalidToken:
            # Handle decryption failure (e.g., incorrect password or corrupted data)
            return None

def load_user_data():
        path = f"C:/{cname}/{appname}/user_data.txt"

        user_data = {
            "first": '2001-01-01',
            "google_id": 1,
            "name": "non",
            "payed": 0
        }

        if not os.path.exists(f"C:/{cname}"):
            os.makedirs(f"C:/{cname}")

        if not os.path.exists(f"C:/{cname}/{appname}"):
            os.makedirs(f"C:/{cname}/{appname}")

        if path and os.path.exists(path):
            with open(path, "rb") as json_file:
                encrypted_data = json_file.read()
                user_data = decrypt_data(encrypted_data)
        else:
            with open(path, "wb") as json_file:
                encrypted_data = encrypt_data(user_data)
                json_file.write(encrypted_data)

        if not os.path.exists(f"C:/{cname}/{appname}/db.sqlite"):
            db_temp = requests.get(f"{appurl}/dbtemp").json()
            with open(f"C:/{cname}/{appname}/db.sqlite", 'w', encoding='latin-1') as file:
                file.write(db_temp['db'])

        return user_data

def load_app_data():
        app_data_path = f"C:/{cname}/{appname}/data.txt"

        if not os.path.exists(f"C:/{cname}"):
            os.makedirs(f"C:/{cname}")

        if not os.path.exists(f"C:/{cname}/{appname}"):
            os.makedirs(f"C:/{cname}/{appname}")

        if os.path.exists(app_data_path):
            with open(app_data_path, 'rb') as file:
                encrypted_data = file.read()
                app_data = decrypt_data(encrypted_data)
        else:
            save_app_data()

        apiurl = app_data.get('url', '')  # Assuming 'url' might not always be present

        return app_data

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

def iscode(code):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/codes') 
    # Query the database to find the user with the matching google_id
    query = ref.order_by_child('code').equal_to(code).limit_to_first(1)

    # Execute the query
    result = query.get()

    if not result:
        # User with the provided google_id not found
        return None

    user_id, user_data = next(iter(result.items()))

    if user_id and not user_data['used']:
        return user_data['plan']
    else:
        return None 

def quittab():
    # Get a list of open browser tabs
    browser_tabs = webbrowser.get().tab_list()

    # Check if any tabs match the condition
    for tab in browser_tabs:
        if tab.url.endswith('/protected_area'):
            # Close the tab if the URL ends with '/protected_area'
            tab.close()

def add_user(user_data):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/users')  # '/users' is the path where you want to store user data

    # Push user data to the database
    new_user_ref = ref.push(user_data)
    
def save_code(code,plan):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/codes')  # '/codes' is the path where you want to store codes

    v= {"code":code,"date":datetime.now().date().isoformat(),'plan':plan,"used":False,"google_id":""}
    # Push the code to the database
    new_code_ref = ref.push(v)
    
def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    characters.replace('"','#')
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def gencode():
    code=f"{generate_strong_password(4)}-{generate_strong_password(4)}-{generate_strong_password(4)}"
    return code

def get_user_info_by_google_id(google_id):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/users')  # '/users' is the path where user data is stored

    # Query the database to find the user with the matching google_id
    query = ref.order_by_child('google_id').equal_to(google_id).limit_to_first(1)

    # Execute the query
    result = query.get()

    if not result:
        # User with the provided google_id not found
        return None

    # The result is a dictionary where keys are unique identifiers (Firebase push IDs)
    # We need to extract the user data from this dictionary
    user_id, user_data = next(iter(result.items()))

    if user_id:
        print("User found:")
        return user_data
    else:
        return None 

def get_db_temp():
    db_content =  get_user_info_by_google_id(1)['db']
    return db_content

def log_me_in(info):
    user_info= get_user_info_by_google_id(info['google_id'])
    path = f"C:/{cname}/{appname}/user_data.txt"
    if user_info:
        with open(f"C:/{cname}/{appname}/db.sqlite", 'w', encoding='latin-1') as file:
            file.write(user_info['db'])
        
        d={}
        for i in user_info:
            if not i == 'db':
                d[i]=user_info[i]
            
        with open(path, 'wb') as file:
            encrypted_data = encrypt_data(d)
            file.write(encrypted_data)
    else:
        user_data = {
            "name": info['name'],
            "google_id": info['google_id'],
            "payed": 0,
            "plan":"free",
            "first": datetime.now().date().isoformat(), 
            'db': get_db_temp()
        }
        add_user(user_data)
        with open(f"C:/{cname}/{appname}/db.sqlite", 'w', encoding='latin-1') as file:
            file.write(user_data['db'])
        del user_data['db']
            
        with open(path, 'wb') as file:
            encrypted_data = encrypt_data(user_data)
            file.write(encrypted_data)
        
def get_user_db_plz(google_id='1'):
    user_data=get_user_info_by_google_id(google_id)

    if user_data and 'db' in user_data:
        return {'db':user_data['db']}
    else:
        try:
            response = requests.get(f"{appurl}/dbtemp")
            response.raise_for_status()  # Raise an exception for bad responses

            db_temp = response.json()
            return db_temp
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve database: {e}")
            response = requests.get(f"{appurl}/dbtempplz")
            response.raise_for_status()  # Raise an exception for bad responses

            db_temp = response.json()
            return db_temp        
        
def add_appds(data):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/pcs')  # '/users' is the path where you want to store user data

    # Push user data to the database
    new_user_ref = ref.push(data)
        
def save_app_data():
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
    app_data = {
        'mac':mac_address,
        "payed": False,
        "plan": "free",
        "first": datetime.now().date().isoformat(),
        "url":appurl
    }
    add_appds(app_data)
    with open(f"C:/{cname}/{appname}/data.txt", 'wb') as txt_file:
        encrypted_data = encrypt_data(app_data)
        txt_file.write(encrypted_data)     

def get_pcs_by_mac(mac):
    # Reference to the Firebase Realtime Database
    ref = db.reference('/pcs')  # '/users' is the path where user data is stored

    # Query the database to find the user with the matching google_id
    query = ref.order_by_child('mac').equal_to(mac).limit_to_first(1)

    # Execute the query
    result = query.get()

    if not result:
        # User with the provided google_id not found
        return None

    # The result is a dictionary where keys are unique identifiers (Firebase push IDs)
    # We need to extract the user data from this dictionary
    user_id, user_data = next(iter(result.items()))

    if user_id:
        print("User found:")
        return user_data
    else:
        return None 

fernet = create_fernet()

@app.route("/")
def home():
    return render_template("errors.html",msg='Are you lost?\n :)',err='Wow')      
            
@app.route("/basic_sub")
def basicsub():
    return render_template("basic.html")

@app.route("/E>t^-sAKY-KX-7NjnHTgIT085oc1j50T7")
def codemebisc():
    code=gencode()
    save_code(code,"basic")
    return render_template('code_gen.html',code=code)

@app.route('/check_bcode', methods=['POST'])
def check_Bactivation_code():
    try:
        # Get the activation code from the request JSON
        data = request.get_json()
        activation_code = data.get('code')
        if activation_code:
            c=iscode(activation_code)
            if c in['basic']:
                global bPay
                bPay=True
                user_info = load_user_data()
                
            
                gid=user_info['google_id'] 
                
                
                ref = db.reference('/codes')
                query = ref.order_by_child('code').equal_to(activation_code).limit_to_first(1)
                result = query.get()
                c_id, c_data = next(iter(result.items()))
        
                c_data['google_id']=gid
                c_data['used']=True
        
                ref.child(c_id).set(c_data)
                return {"result":'accepted'}
            else:
                return {"result":'fail'}
        else:
            return {"result":'fail'}

    except Exception as e:
        return render_template("errors.html",msg=str(e),err='Unexpected')
    
@app.route('/backup_database', methods=['POST'])
def backup_database():
        # Get the activation code from the request JSON
        data = request.get_json()
        datab = data.get('db')
        if datab:
                user_info = load_user_data()
                
            
                gid=user_info['google_id'] 
                
                
                ref = db.reference('/users')
                query = ref.order_by_child('google_id').equal_to(gid).limit_to_first(1)
                result = query.get()
                c_id, c_data = next(iter(result.items()))
        
                c_data['db']=datab
        
                ref.child(c_id).set(c_data)
                return jsonify({"message": "Database backup successful"}), 200
        else:
            return jsonify({"error":"no data base found"}), 500
            
@app.route("/pay_basic")
def paybasic():
    logged_in = "google_id" in session
    if logged_in:
        try:
            paypalrestsdk.configure({
            "mode": "live",  # Use "live" in production
            "client_id": "AUQ3jts3ZsApuFdAuwnCIcVX2MMKQ3qySgD9lcakX24lSJgRjRbNV_0aLZOfI66iG0AjXDq2YbxRidxZ",
            "client_secret": "EK5Aafqm0YaIZyoYpd5uE2MfWcwBjt3aRzBG46L0X-DZT7rogN5MGZavCGHLiFZ2BxuwtC8c2hKAuEFF"
            })
            payment = Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": f"{basicprice}.00",
                        "currency": "USD"
                    }
                }],
                "redirect_urls": {
                    "return_url": f"{appurl}/basic_success",
                    "cancel_url": f"{appurl}/basic_cancel"
                }
            })

            if payment.create():
                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = link.href
                        global bPay
                        bPay=True
                        return redirect(redirect_url)
            else:
                error_message = f"Error: {payment.error}"
                return render_template("errors.html",msg=error_message,err='Unexpected')
        except Exception as e:
            return render_template("errors.html",msg=e,err='Unexpected')
    else:
        return render_template("errors.html",msg="User not logged in",err='Unexpected')
    
@app.route("/basic_success")
def basic_success():
    global bPay
    if bPay:
        app_data = load_app_data()
        
        user_info = load_user_data()
            
        # Check if 'plan' is present in app_data
        if 'plan' in app_data:
            # Set 'plan' to 'basic'
            app_data['plan'] = 'basic'
            app_data['payed'] = True

            # Check if user_info is found
            if user_info:
                # Check if the current plan is 'free'
                if user_info.get('plan', '') == 'free'or not 'plan' in user_info:
                    # Set 'plan' to 'basic' and update 'payed' with the amount paid
                    user_info['plan'] = 'basic'
                    user_info['payed'] = basicprice 
                
                    user_id = user_info['google_id']
                    ref = db.reference('/users')
                    query = ref.order_by_child('google_id').equal_to(user_id).limit_to_first(1)
                    result = query.get()
                    user_id, user_data = next(iter(result.items()))
                    ref = db.reference('/users/'+ user_id)
                    ref.set(user_info)
                    
                    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
                    ref = db.reference('/pcs')
                    query = ref.order_by_child('mac').equal_to(mac).limit_to_first(1)
                    result = query.get()
                    user_id, user_data = next(iter(result.items()))
                    ref = db.reference('/pcs/'+ user_id)
                    ref.set(app_data)
                
                    # Save the updated user information to the local JSON file
                    path = f"C:/{cname}/{appname}/user_data.txt"
                    with open(path, 'wb') as file:
                        ed=encrypt_data(user_info)
                        file.write(ed)
                    
                    path = f"C:/{cname}/{appname}/data.txt"
                    with open(path, 'wb') as file:
                        ed=encrypt_data(app_data)
                        file.write(ed)

                    # Return a response indicating success
                    bPay=False
                    return render_template("pay_sucsess.html")
                else:
                    bPay=False
                    return render_template("pay_sucsess.html")
            else:
                bPay=False

                # Return a response indicating that the user information is not found
                return render_template("errors.html",msg="User information not found.",err='Unexpected')
        else:
            bPay=False
            # Return a response indicating that 'plan' is not present in app_data
            return render_template("errors.html",msg="'plan' not present in app_data.",err='Unexpected')
    else:
        return render_template("errors.html",msg="payment did not go through.",err='Unexpected')
        
@app.route("/urlme")
def urlme():
    path = f"C:/{self.cname}/{self.appname}/data.txt"
    app_data = load_app_data()
    if os.path.exists(f"C:/{cname}") and os.path.exists(f"C:/{cname}/{appname}") and  'plan' in app_data:
        # Set 'plan' to 'basic'
        app_data['url'] = appurl
        with open(path, 'wb') as file:
            ed=encrypt_data(app_data)
            file.write(ed)
    else:
        return render_template("app_error.html")

@app.route("/basic_cancel")
def pay_cancel():
    # Handle canceled payment
    return render_template("Payment_canceled.html")

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/app_data_me")
def app_data_me():
    mac= ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
    c=get_pcs_by_mac(mac)
    if c :
        with open(f"C:/{cname}/{appname}/data.txt", 'wb') as txt_file:
            encrypted_data = encrypt_data(c)
            txt_file.write(encrypted_data) 
    else:
        save_app_data()
    return 'hi'

@app.route("/dbtempplz")
def dbtempplz():
    db_content =  get_user_info_by_google_id(10)['db']
    db={'db':db_content}
    return db

@app.route("/dbtemp")
def dbtemp():
    db={'db':get_db_temp()}
    return db

@app.route("/dbmeplz")
def dbmeplzz():
    path=f'c:/{cname}/{appname}/user_data.txt'
    if os.path.exists(path):
        user_data = load_user_data()
        google_id=user_data['google_id']
        c=get_user_db_plz(google_id)
    else:
        c=get_user_db_plz()
    return c
        
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["donee"]=True
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    session["donee"]=False
    return redirect("/logme")

@app.route("/logme")
def index():
    return render_template("login.html")

@app.route("/protected_area")
@login_is_required
def done():
    logged_in = "google_id" in session
    if logged_in:
        google_id = session.get("google_id")
        name = session.get("name")
        info={"google_id":google_id,"name":name}
        try:
            log_me_in(info)
            #quittab()
            return render_template("loged_in.html")
        except Exception as e:
            return render_template("errors.html",msg=str(e),err='Unexpected')
    return render_template("loged_in _error.html")

if __name__ == "__main__":
    app.run(debug=True)


