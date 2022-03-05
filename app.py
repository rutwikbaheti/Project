# from urllib import response
# from flask import Flask, redirect,request,render_template, jsonify, url_for
# from flask_pymongo import pymongo
# from flask_session import Session
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority")
db = client.DataBase
records = db.User_Info

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/registration", methods=['post', 'get'])
def registration():
    message = ''
    if "email" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('home.html', email=new_email)
    return render_template('registration.html')

# dbUrl = "mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority"
# client = pymongo.MongoClient(dbUrl)
# db = client.get_database('DataBase')

# app = Flask(__name__)

# Session(app)

# @app.route('/')
# def index():
#     return render_template("home.html")

# @app.route('/home', methods=["POST"])
# def home():
#     return render_template("home.html")

# @app.route('/login', methods=["GET","POST"])
# def login():
#   if(request.method == "POST"):
#     user = db.User_Info.find_one({
#       "email": request.form.get('email')
#     })
#     session["name"] = request.form.get("email")
#     if user["password"] == request.form.get("password"):
#       return render_template("home.html")
#     else : 
#       return jsonify({ "error": "Incorrect Password" }), 403
#   return render_template("login.html") 

# @app.route('/register', methods=["GET","POST"])
# def register():
#   if(request.method == "POST"):
#     user = {
#         "email" : request.form.get("email"),
#         "password" : request.form.get("password")
#     }
#     if db.User_Info.find_one({ "email": user['email'] }):
#       return jsonify({ "error": "Email address already in use" }), 400
#     else:  
#       db.User_Info.insert_one(user)
#       return home()
#   return render_template("registration.html")
     
# if __name__ == '__main__':
#     app.run(debug=True)





@app.route('/home')
def home():
    if "email" in session:
        email = session["email"]
        return render_template('home.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
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
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("index.html")
    else:
        return render_template('index.html')

if __name__ == "__main__":
  app.run(debug=True)