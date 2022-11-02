import pyrebase
from flask import render_template, request, redirect, session, url_for
from app import app
import os
import pandas as pd
import numpy as np
import random

APIKEY = os.environ['APIKEY']

config = {
  'apiKey': APIKEY,
  'authDomain': "petriplanets.firebaseapp.com",
  'projectId': "petriplanets",
  'databaseURL':"https://petriplanets-default-rtdb.europe-west1.firebasedatabase.app/",
  'storageBucket': "petriplanets.appspot.com",
  'messagingSenderId': "24272774167",
  'appId': "1:24272774167:web:509a1f66cc560c05bd2852",
  'measurementId': "G-78J2NWZ869"
}

app.secret_key="hello"

df=pd.read_excel("database2.xlsx")
likes_data=np.zeros(df.shape[0]).tolist()



with open('introduction.txt', 'r') as file:
    introduction = file.read()

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

db=firebase.database()
storage=firebase.storage()

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            try:
                user=auth.sign_in_with_email_and_password(email, password)
                name=db.child(user['localId']).child("Handle").get().val()
                randnum=random.randint(0, (df.shape[0]-1)) 
                image =df["url"][0]
                planet_name = df["Name"][0]
                planet_story = df["stories"][0]
                like_status=0
                with open('introduction.txt', 'r') as file:
                    introduction = file.read()
                session["user"]= user
                session["name"]= name
                session["image"]= image
                session["introduction"]= introduction
                session["user"]= user 
                session["randnum"]= randnum  
                session["planet_name"]= planet_name   
                session["planet_story"]= planet_story
                session["like_status"]= like_status      
                session["like_status_list"]= likes_data            

                #user_id = auth.get_account_info(user['idToken'])
                #session['usr'] = user_id
                return redirect(url_for("home"))
            except:
                unsuccessful = 'Please check your credentials'
                return render_template('index.html', umessage=unsuccessful)
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])
            db.child(user['localId']).child("likes").set(likes_data)            
            auth.create_user_with_email_and_password(email, password)
            return render_template('index.html')
    return render_template('create_account.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
            email = request.form['name']
            auth.send_password_reset_email(email)
            return render_template('index.html')
    return render_template('forgot_password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):
        return redirect(url_for("main"))
    else:
        return render_template('home.html', nametest=session["name"], introduction=session["introduction"])

@app.route('/main', methods=['GET', 'POST'])
def main():
    if (request.method == 'POST' and request.form['action'] == "Travel to the next planet"):    
        session.pop("image", None)
        session.pop("planet_name", None)
        session.pop("planet_story", None)
        session.pop("randnum", None)
        session.pop("like_status_list", None)
        session.pop("like_status", None)
        session["randnum"]=random.randint(0, (df.shape[0]-1))
        session['like_status_list']=db.child(session["user"]['localId']).child("likes").get().val()
        session['like_status']=session['like_status_list'][session["randnum"]]
        session["image"]=df["url"][session["randnum"]]
        session["planet_name"]= df["Name"][session["randnum"]]
        session["planet_story"]= df["stories"][session["randnum"]]     
        return render_template('main.html', img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])
    elif (request.method == 'POST' and request.form['action'] == "Like"):
        session.pop("like_status", None)
        session['like_status']=1
        db.child(session["user"]['localId']).child("likes").update({session["randnum"]:1})
        return render_template('main.html', img=session["image"] , like_status=session['like_status'], planet_name=session["planet_name"], planet_story=session["planet_story"])


    elif (request.method == 'POST' and request.form['action'] == "Dislike"):
        session.pop("like_status", None)
        session['like_status']=-1
        db.child(session["user"]['localId']).child("likes").update({session["randnum"]:-1})
        return render_template('main.html', img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])


    else:
        return render_template('main.html', img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])


if __name__ == '__main__':
    app.run(debug=True)
