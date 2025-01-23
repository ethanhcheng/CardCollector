from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/login')
def login():
    return render_template('login.hteml')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/collection')
def collection():
    return 'Collection'

@app.route('/sets')
def sets():
    return 'Sets'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)