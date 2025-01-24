from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://mongodb:27017/")
db = client["CardCollector"]

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/collection')
def collection():
    return 'Collection'

@app.route('/sets')
def sets():
    return 'Sets'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)