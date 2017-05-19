from flask import Flask, render_template, redirect, session, flash, request
app = Flask(__name__)
app.secret_key = "churros"
from mysqlconnection import MySQLConnector
mysql = MySQLConnector(app, 'login_registration')
import md5
import re

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=["POST"])
def register_user():

    flag = True # will remain True, if no errors were detected

    # Not blank
    if len(request.form['first_name']) < 1:
        flag = False
        flash("Your entry for first name must not be blank.")
    if len(request.form['last_name']) < 1:
        flag = False
        flash("Your entry for last name must not be blank.")
    # Longer than 2 char
    if len(request.form['first_name']) < 3:
        flag = False
        flash("Your entry for first name must ne longer than 2 characters.")
    if len(request.form['last_name']) < 3:
        flag = False
        flash("Your entry for last name must be longer than 2 characters.")
    # all letters
    if not request.form["first_name"].isalpha() and not request.form["last_name"].isalpha():
        flag = False
        flash("Your first name and last name must be letters only")
    # email is valid
    if not email_regex.match(request.form['email']):
        flag = False
        flash("Your email is not valid.")
    # len password > 8
    if len(request.form['password']) < 8:
        flag = False
        flash("Your password must be 8 characters long.")
    # passwords match
    if request.form['password'] != request.form['c_password']:
        flag = False
        flash("Your passwords don't match.")

    if flag:
        print "User info is good."
        query = "INSERT into users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"

        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest()
        }

        session['user_id'] = mysql.query_db(query, data) # store in session logged in users id
        return redirect("/success")

    else:
        print "User info had errors."
        return redirect("/")

@app.route('/login', methods=["POST"])
def login():
    if len(request.form['email']) < 1 or len(request.form['password']) < 1: # if either loing field blank redirect
        flash("You must enter both email and password.")
        return redirect("/")
    else:
        query = "SELECT * from users WHERE email = :email"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        print user

        if user:
            if user[0]['password'] == md5.new(request.form['password']).hexdigest():
                session['user_id'] = user[0]['id']
                return redirect("/success")
            else:
                flash("Your password is invalid.")
                return redirect("/")
        else:
            flash("Your email is not valid.")
            return redirect("/")



@app.route("/success")
def success():
    try:
        query = "SELECT * from users WHERE id=:user_id"
        data = {
            'user_id': session['user_id']
        }

        logged_in_user = mysql.query_db(query, data)

        print logged_in_user
        return render_template("success.html", logged_in_user = logged_in_user)
    except:
        return redirect("/")


app.run(debug=True)
