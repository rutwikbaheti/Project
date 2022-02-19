from flask import Flask,request,render_template
from flask_pymongo import pymongo

dbUrl = "mongodb+srv://admin:admin@cluster0.u36vn.mongodb.net/DataBase?retryWrites=true&w=majority"
client = pymongo.MongoClient(dbUrl)
db = client.get_database('DataBase')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)