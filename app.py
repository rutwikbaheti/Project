from urllib import response
from flask import Flask, redirect,request,render_template, jsonify, url_for
from flask_pymongo import pymongo
from flask_session import Session

dbUrl = "mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority"
client = pymongo.MongoClient(dbUrl)
db = client.get_database('DataBase')

app = Flask(__name__)

Session(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home', methods=["POST"])
def home():
    return render_template("home.html")

@app.route('/login', methods=["GET","POST"])
def login():
  if(request.method == "POST"):
    user = db.User_Info.find_one({
      "email": request.form.get('email')
    })
    session["name"] = request.form.get("email")
    if user["password"] == request.form.get("password"):
      return render_template("home.html")
    else : 
      return jsonify({ "error": "Incorrect Password" }), 403
  return render_template("login.html") 

@app.route('/register', methods=["GET","POST"])
def register():
  if(request.method == "POST"):
    user = {
        "email" : request.form.get("email"),
        "password" : request.form.get("password")
    }
    if db.User_Info.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400
    else:  
      db.User_Info.insert_one(user)
      return home()
  return render_template("registration.html")
     
if __name__ == '__main__':
    app.run(debug=True)