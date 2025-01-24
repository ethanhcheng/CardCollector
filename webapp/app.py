from flask import Flask, render_template, jsonify, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key="secret_key"

client = MongoClient("mongodb://mongodb:27017/")
db = client["CardCollector"]
users = db["Users"]

login_manager = LoginManager()
login_manager.login_view = "start"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = users.collection.find_one({"_id": user_id})
    if user_data:
        return User(id=user_data["_id"], username=user_data["username"])
    return None

@app.route('/')
def start():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('start.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = users.find_one({"username": username})
        if user_data and bcrypt.checkpw(password.encode("utf-8"), user_data["password"]):
            user = User(id=user_data["_id"], username = username)
            login_user(user)
            return redirect(url_for('home'))
        flash("Invalid Password")
    return render_template('login.html')

@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.find_one({"username": username}):
            flash("Username already taken")
        else: 
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_id = users.insert_one({"username": username, "password": hashed}).inserted_id
            user = User(id = user_id, username = username)
            login_user(user)
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/home')
def home():
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('home.html', username=username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("start"))

@app.route('/collection')
@login_required
def collection():
    return 'Collection'

@app.route('/sets')
def sets():
    return 'Sets'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)