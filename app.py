import pyrebase
from flask import Flask, render_template, request, redirect, session, url_for
import os
import pandas as pd
import numpy as np
import random
import openai

app = Flask(__name__)

APIKEY = os.environ['APIKEY']
APIKEY2 = os.environ['APIKEY2']

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


def gpt3(prompt_text):
    openai.api_key= APIKEY2
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt_text,
            temperature=0.95,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    )
    content = response.choices[0].text.split('.')
    return response.choices[0].text

app.secret_key="hello"

df=pd.read_excel("database3.xlsx")
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
                prompt=""
                answer=""
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
                session["prompt"]= prompt
                session["answer"]= answer            
            

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
            handle = request.form['username']
            auth.create_user_with_email_and_password(email, password)
            user=auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])
            db.child(user['localId']).child("likes").set(likes_data)             
            return render_template('index.html', smessage=1)
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
    if (request.method == 'POST'):
        if ("action" in request.form):    
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
        elif ("action1" in request.form): 
            session.pop("like_status", None)
            session['like_status']=1
            db.child(session["user"]['localId']).child("likes").update({session["randnum"]:1})
            return render_template('main.html', img=session["image"] , like_status=session['like_status'], planet_name=session["planet_name"], planet_story=session["planet_story"])


        elif ("action2" in request.form): 
            session.pop("like_status", None)
            session['like_status']=-1
            db.child(session["user"]['localId']).child("likes").update({session["randnum"]:-1})
            return render_template('main.html', img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])
        
        elif ("action3" in request.form): 
            return redirect(url_for('colony'))
    
        elif ("action4" in request.form): 
            question = request.form['action4']
            session.pop("prompt", None)
            session.pop("answer", None)
            session["prompt"]="Your information: "+session["planet_story"]+"The question asked:"+question
            session["answer"]=gpt3(session["prompt"])
            return render_template('main.html', img=session["image"], answer=session["answer"], like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])
        

    else:
        return render_template('main.html', img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])

@app.route('/colony', methods=['GET', 'POST'])
def colony():
    if (request.method == 'POST'):
        return redirect(url_for("main"))
    else:
        return render_template('colony.html', name=session["name"] , planet_name=session["planet_name"])



if __name__ == '__main__':
    app.run(debug=True)
