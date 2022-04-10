from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import pandas as pd
import numpy as np
import pickle
from bson import ObjectId 
from datetime import datetime

app = Flask(__name__)
model = pickle.load(open('model.pkl','rb'))
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority")
db = client.DataBase
records = db.User_Info
test=pd.read_csv("Testing.csv",error_bad_lines=False)
x_test=test.drop('prognosis',axis=1)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile',methods=["GET","POST"])
def profile():
    if "email" in session:
        user = db.User_Info.find_one({"email" : session["email"]})
        if request.method == "POST":
            db.User_Info.update_many({"email" : session["email"]},
            {"$set" : 
            {"name": request.form['name'],
            "phone": request.form['phone'],
            "dob": request.form['dob'],
            "gender": request.form['gender'],
            "blood_group": request.form['blood_group']}
            })
            return redirect(url_for('profile',user=user))
    return render_template('profile.html',user = user )

@app.route("/update")
def update ():
    if "email" in session:
        user = db.User_Info.find_one({"email" : session["email"]})
    return render_template('update.html',user = user )

@app.route("/action3", methods=['POST'])
def action3():
    if "email" in session:
        profileInfo = request.args.get('form')
        id =request.form['_id']
        name=request.form['name']
        gender=request.form["gender"]
        blood_group=request.form["blood_group"]
        phone=request.form['phone']
        records.update_one(
        { "_id": ObjectId(id) },
        { "$set": { "name": name,"phone":phone,"gender": gender,"blood_group":blood_group}})
        return redirect(url_for("home"))


@app.route("/history")
def history():
    if "email" in session:
        user = db.User_Info.find_one({"email" : session["email"]})
        if 'history' in user :
            history_list = user['history']
        else:
            history_list = {}    
    return render_template('history.html',history_list = history_list)

@app.route("/registration", methods=['post', 'get'])
def registration():
    message = ''
    if "email" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        blood_group = request.form.get("blood_group")
        phone = request.form.get("phone")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            redirect(url_for('index', message=message))
        if email_found:
            message = 'This email already exists in database'
            redirect(url_for('index', message=message))
        if password1 != password2:
            message = 'Passwords should match!'
            redirect(url_for('index', message=message))
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email,'dob':dob,'gender':gender,'blood_group':blood_group,'phone':phone, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            return redirect(url_for('login', email=new_email))
    return render_template('registration.html')

@app.route('/home')
def home():
    if "email" in session:
        email = session["email"]
        return render_template('home.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    message = ""#'Please login to your account'
    if "email" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('home'))
            else:
                if "email" in session:
                    return redirect(url_for("home"))
                message = 'Wrong password'
                return redirect(url_for('login', message=message))
                #return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return redirect(url_for('login', message=message))
            #return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

data = {}

@app.route('/diagnosis',methods=["GET"])
def diagnosis():
    return render_template("diagnosis.html")  

@app.route('/diagnosis_0',methods=["GET","POST"])
def diagnosis_0():
    if request.method == 'POST':
        if request.form['user_identity'] == 'myself':
            user = db.User_Info.find_one({"email" : session["email"]})
            data['name'] = user["name"]
            data['dob'] = user["dob"]
            data['gender'] = user["gender"]
            data['blood_group'] = user["blood_group"]
            return redirect(url_for('diagnosis_2'))
        else:    
            return redirect(url_for('diagnosis_1'))
    return render_template("diagnosis_0.html") 

@app.route('/diagnosis_1',methods=["GET","POST"])
def diagnosis_1():
    if request.method=='POST':
        data['name'] = request.form['name']    
        data['dob'] = request.form['dob']
        data['gender'] = request.form['gender']
        data['blood_group'] = request.form['blood_group']
        return redirect(url_for('diagnosis_2'))
    return render_template("diagnosis_1.html") 

@app.route('/diagnosis_2',methods=["GET","POST"])
def diagnosis_2():
    if request.method=='POST':
        col=x_test.columns
        inputt = [str(x) for x in request.form.values()]
        b=[0]*114
        for x in range(0,114):
            for y in inputt:
                if(col[x]==y):
                    b[x]=1
        b=np.array(b)
        b=b.reshape(1,114)
        prediction = model.predict(b)
        prediction=prediction[0]
        data['prediction'] = prediction
        data['date-time'] = datetime.now()
        print("Prediction : " + prediction)
        return redirect(url_for('diagnosis_3'))
    return render_template("diagnosis_2.html") 

@app.route('/diagnosis_3',methods=["GET","POST"])
def diagnosis_3():
    if request.method=='POST':
        data['diabetes'] = request.form['diabetes']
        data['history_of_alcohol_consumption'] = request.form['history_of_alcohol_consumption'] 
        data['yellow_urine'] = request.form['yellow_urine']
        data['unsteadiness'] = request.form['unsteadiness']
        return redirect(url_for('result'))
    return render_template("diagnosis_3.html") 

@app.route('/result',methods=["GET","POST"])
def result():
    if "email" in session:
        db.User_Info.update_one({"email":session["email"]},{ "$push" :{"history":data}})
        print(session["email"])    

        dis = db.Disease_Info.find_one({"disease name" : data['prediction']})
        info = dis['information']
        cause = dis['causes']
        doc = db.Doctor_Info.find_one({"disease name" : data['prediction']})
    return render_template("result.html",pred="{}".format(data['prediction']), info = info, cause = cause, data = data, doc=doc) 

if __name__ == "__main__":
  app.run()