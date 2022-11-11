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
            presence_penalty=0.5
    )
    content = response.choices[0].text.split('.')
    return response.choices[0].text

app.secret_key="hello"

df=pd.read_excel("database3.xlsx")
likes_data=np.zeros(df.shape[0]).tolist()
chat_data=np.zeros(2).tolist()


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
                chats=""
                chats2=""
                idx=0
                num_visitors=0
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
                session["num_visitors"]= num_visitors   
                session["chats"]= chats
                session["chats2"]= chats2      
                session["idx"]= idx   
            

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
            db.child(user['localId']).child("visited").set(likes_data)                 
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
            session.pop("prompt", None)   
            session.pop("image", None)
            session.pop("planet_name", None)
            session.pop("planet_story", None)
            session.pop("randnum", None)
            session.pop("like_status_list", None)
            session.pop("like_status", None)
            session.pop("num_visitors", None)
            session["randnum"]=random.randint(0, (df.shape[0]-1))
            if db.child(session["user"]['localId']).child("visited").child(session["randnum"]).get().val()==1:
                session.pop("randnum", None)
                session["randnum"]=random.randint(0, (df.shape[0]-1))
                if db.child(session["user"]['localId']).child("visited").child(session["randnum"]).get().val()==1:
                    session.pop("randnum", None)
                    session["randnum"]=random.randint(0, (df.shape[0]-1))
            session['like_status_list']=db.child(session["user"]['localId']).child("likes").get().val()
            session['like_status']=session['like_status_list'][session["randnum"]]
            session["image"]=df["url"][session["randnum"]]
            session["planet_name"]= df["Name"][session["randnum"]]
            session["planet_story"]= df["stories"][session["randnum"]]
            db.child(session["user"]['localId']).child("visited").update({session["randnum"]:1})
            session["num_visitors"]=db.child("visitors").child(session["randnum"]).get().val()
            session["num_visitors"]+=1
            db.child("visitors").update({session["randnum"]:session["num_visitors"]})   
            return render_template('main.html', visitors=session["num_visitors"], img=session["image"],user_name=session["name"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])
            
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
    
        elif ("action5" in request.form): 
            return redirect(url_for('liked'))        

        elif ("action7" in request.form):
            if db.child(session["user"]['localId']).child("planets").child(session["planet_name"]).child(0).get().val() == "":
                session.pop("answer", None) 
                session.pop("chat", None)
                session.pop("chat2", None)
                session["chats"]="<p>"+session["planet_story"]+"</p>" 
                session["chats2"]=session["planet_story"]
                session["answer"]=""
                return redirect(url_for('chat')) 
            elif db.child(session["user"]['localId']).child("planets").child(session["planet_name"]).child(0).get().val() == None:
                session.pop("answer", None) 
                session.pop("chat", None)
                session.pop("chat2", None)
                session["chats"]="<p>"+session["planet_story"]+"</p>" 
                session["chats2"]=session["planet_story"]
                session["answer"]=""
                return redirect(url_for('chat')) 
            else:
                print("klopt niet")
                session.pop("answer", None) 
                session.pop("chat", None)
                session.pop("chat2", None)
                session["chats"]= db.child(session["user"]['localId']).child("planets").child(session["planet_name"]).child(0).get().val()
                session["chats2"]= db.child(session["user"]['localId']).child("planets").child(session["planet_name"]).child(1).get().val()
                session["answer"]=""
            return redirect(url_for('chat'))        


    else:  
        return render_template('main.html', visitors=session["num_visitors"], user_name=session["name"], img=session["image"] , like_status=session['like_status'] , planet_name=session["planet_name"], planet_story=session["planet_story"])
        
      

@app.route('/colony', methods=['GET', 'POST'])
def colony():
    if (request.method == 'POST'):
        return redirect(url_for("main"))
    else:
        return render_template('colony.html', name=session["name"] , planet_name=session["planet_name"])

@app.route('/liked', methods=['GET', 'POST'])
def liked():
    if (request.method == 'POST'):
        if ("action6" in request.form):
            return redirect(url_for("main"))
        else:
            pass
    else:
        like_list=[]
        for i in range(df.shape[0]):            
            if db.child(session["user"]['localId']).child("likes").child(i).get().val()==1:
                    temp_list=[df.url[i],df.Name[i]]
                    like_list.append(temp_list)            
        return render_template('liked.html', likes=like_list)

@app.route('/main/<planet>', methods=['GET', 'POST'])
def planet(planet):
    try:
        session["idx"]=int(df.index[df['Name']==planet].values)
    except TypeError:
        pass

    session.pop("image", None)
    session.pop("planet_name", None)
    session.pop("planet_story", None)
    session.pop("randnum", None)
    session.pop("like_status_list", None)
    session.pop("like_status", None)
    session.pop("num_visitors", None)
    session['like_status_list']=db.child(session["user"]['localId']).child("likes").get().val()
    session['like_status']=session['like_status_list'][session["idx"]]
    session["image"]=df["url"][session["idx"]]
    session["planet_name"]= df["Name"][session["idx"]]
    session["planet_story"]= df["stories"][session["idx"]]
    db.child(session["user"]['localId']).child("visited").update({session["idx"]:1})
    session["num_visitors"]=db.child("visitors").child(session["idx"]).get().val()
    session["num_visitors"]+=1
    return redirect(url_for("main"))

@app.route('/chat', methods=['GET', 'POST'])
def chat(): 
    if (request.method == 'POST' and "action9" in request.form):
        return redirect(url_for("main"))
    elif (request.method == 'POST' and "action10" in request.form):
        question = request.form['action10'] 
        session.pop("prompt", None)            
        session["prompt"]=question
        session["chats"]+= "<br><h3>"+session["prompt"]+"</h3> <br>"
        session["chats2"]+= session["prompt"]+". "
        session.pop("answer", None)  
        session["answer"]=gpt3(session["chats2"])
        session["chats"]+= "<br> <p>"+session["answer"]+"</p> <br>"
        session["chats2"]+= session["answer"]+". "  
        db.child(session["user"]['localId']).child("planets").child(session["planet_name"]).set({0:session["chats"], 1:session["chats2"]})
        return render_template('conversation.html', planet_name=session["planet_name"], answer=session["answer"], chat=session["chats"])
    else:    
        return render_template('conversation.html',planet_name=session["planet_name"], chat=session["chats"])

if __name__ == '__main__':
    app.run(debug=True)
