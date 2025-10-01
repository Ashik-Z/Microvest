from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "be5f1f442394779ce1bf2162b062e637"

app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = '123456'
app.config["MYSQL_DB"] = 'microvest'

mysql = MySQL(app)


# Route for handling the login page logic
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))

        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            return render_template('index.html', msg = "Logged in successfully!")

        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg)



# Route for handling logout
@app.route('/logout')
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for('login'))



# Route for handling the registration page logic
@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        account = cursor.fetchone()

        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        email_exists = cursor.fetchone()

        if account:
            msg = 'Username already exists!'
        elif email_exists:
            msg = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not request.form["password"] or not email:
            msg = 'Please fill out the form!'
        else:
            raw_password = request.form['password']
            hashed_password = generate_password_hash(raw_password, method='pbkdf2:sha256')
            cursor.execute("INSERT INTO user (username, password, email) VALUES (%s, %s, %s)",
                           (username, hashed_password, email)
                           )
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg = msg)



if __name__ == "__main__":
    app.run(debug=True)