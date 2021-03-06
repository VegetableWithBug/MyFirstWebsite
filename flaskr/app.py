# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request,session,redirect,flash
from functools import wraps
# create the application object
app = Flask(__name__)

app.secret_key = "my precious"

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    return render_template('index.html')  # return a string

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.username != 'admin' or request.password != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were just logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
   session.pop('logged_in',None)
   return redirect(url_for('welcome'))

@app.route('/register')
def register():
    return render_template('register.html')

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)