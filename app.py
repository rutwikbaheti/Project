from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import pandas as pd
import numpy as np
import pickle
from bson import ObjectId 
from datetime import datetime
from flask_mail import Mail,Message
from random import randint
import re

from requests import Session

app = Flask(__name__)
mail=Mail(app)

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='diagnosoft.app@gmail.com'
app.config['MAIL_PASSWORD']='Pass@123'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)

model = pickle.load(open('model.pkl','rb'))
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority")
db = client.DataBase
records = db.User_Info

@app.route('/')
@app.route('/index')
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
        pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
        val_pass = re.findall(pattern, password1)
        
            
        email_found = records.find_one({"email": email})
        if email_found:
            message = "This email already exists"
            return redirect(url_for('registration', message=message))
        elif password1 != password2:
            message = "Passwords should be same"
            return redirect(url_for('registration', message=message))
        elif not val_pass:
            message="Password must be at least 8 characters containing capital letters[A-Z], small letters[a-z], symbols[@#$%^&] and numbers[0-9]"
            return redirect(url_for('registration', message=message))
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

@app.route("/forget_password", methods=["POST","GET"])
def forget_password():
    message=""
    if request.method == 'POST':
        email = request.form.get("email")
        email_found = db.User_Info.find_one({"email": email})
        if email_found:
            msg=Message(subject='Change Password OTP',
            sender='diagnosoft.app@gmail.com',recipients=[email])
            otp=randint(000000,999999)
            msg.body=str(otp)
            mail.send(msg)
            hashed_otp = otp
            return render_template("/otp_verification.html",email=email_found['email'],otp=hashed_otp)
        else:
            message="Email not found"
            return redirect(url_for("forget_password",message=message))    
    return render_template("forget_password.html")

@app.route("/otp_verification", methods=["POST","GET"])
def otp_verification():
    message=""
    if request.method == 'POST':
        print("otp"+request.form.get("otp"))
        print("hashed" + request.form.get("hashed"))
        print(request.form.get("otp")==request.form.get("hashed"))
        if(request.form.get("otp")==request.form.get("hashed")):
            return redirect(url_for("new_password",email=request.form['email']))
        else:
            message = "Invalid OTP"
            return render_template("/otp_verification.html",message=message,email=request.form.get("email"),otp=request.form.get("hashed"))
    return render_template("otp_verification.html")   

@app.route("/new_password" ,methods=["POST","GET"])
def new_password():
    message=""
    if request.method == 'POST':
        if(request.form['password'] == request.form['re_password']):
            hashed = bcrypt.hashpw(str(request.form['password']).encode('utf-8'), bcrypt.gensalt())
            db.User_Info.update_one({"email" : request.form['email']},{'$set' : {'password' : hashed}})
            return redirect(url_for("login"))
        else:
            message = "Password must be same as re-entered password"
            return redirect(url_for("new_password",message=message,email=request.form['email']))    
    return render_template("new_password.html")

@app.route("/change_password", methods=["POST","GET"])
def change_password():
    message=""
    if request.method == 'POST':
        if "email" in session:
            user = db.User_Info.find_one({"email":session["email"]})
            if bcrypt.checkpw(request.form.get("old_password").encode('utf-8'), user['password']):
                if(request.form.get('password') == request.form.get("re_password")):
                    hashed = bcrypt.hashpw(str(request.form['password']).encode('utf-8'), bcrypt.gensalt())
                    db.User_Info.update_one({"email":session["email"]},{"$set":{"password" : hashed}})
                    return redirect(url_for("home"))
                else:
                    message="New password must be same as re-entered password"
                    return redirect(url_for("change_password",message=message))
            else:      
                message="Old password is incorrect"
                return redirect(url_for("change_password",message=message))  
    return render_template("change_password.html")

@app.route("/delete_account", methods=["POST", "GET"])
def delete_account():
    if "email" in session:
        db.User_Info.delete_one({"email":session["email"]})
        session.pop("email", None)
    return redirect(url_for("index"))
    
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
        col=['itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 'joint_pain', 'stomach_pain', 'acidity', 'vomiting', 'burning_micturition', 'spotting_ urination', 'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy', 'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellowing_of_eyes', 'swelling_of_stomach', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness', 'loss_of_balance', 'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration', 'visual_disturbances', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze']
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
  app.run(debug=True)