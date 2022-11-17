import pandas as pd
from flask import Flask, render_template,  request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pickle
from flask_cors import CORS,cross_origin
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from sklearn.compose import ColumnTransformer

app = Flask(__name__)
data = pd.read_csv('Cleaned_Car_data.csv')
model=pickle.load(open('LinearRegressionModel.pkl','rb'))


# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '92.205.12.247'
app.config['MYSQL_USER'] = 'python_crud'
app.config['MYSQL_PASSWORD'] = 'python_crud'
app.config['MYSQL_DB'] = 'python_crud'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/login/', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            session['password'] = account['password']


            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html',title="Login")


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM user WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s)', (email,username, password))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html',title="Register")

# http://localhost:5000/pythinlogin/home 
# This will be the home page, only accessible for loggedin users


@app.route('/')
def home():

    
    companies = sorted(data['company'].unique())
    car_models = sorted(data['name'].unique())
    year = sorted(data['year'].unique(), reverse=True)
    fuel_type = data['fuel_type'].unique()

    companies.insert(0,'Select Company')

    # prediction all from database 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM prediction')
    prediction = cursor.fetchall()

    # reviews from db
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM reviews')
    reviews = cursor.fetchall()

    print(prediction)



    # company= request.args.get('company') 
    # car_model=request.args.get('car_models')
    # years=request.args.get('year')
    # fuel_types =request.args.get('fuel_type')
    # driven=request.form.get('kilo_driven')

    
    # # prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
    # #                           data=np.array([car_model,company,years,driven,fuel_types]).reshape(1, 5)))

    # if company is None:
    #     output=None
    # else:
    #     prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
    #                           data=np.array([car_model,company,years,driven,fuel_types]).reshape(1, 5)))
    #     output=round(prediction[0],2)
    #     # print(output)



    # print(model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'])))

    if not session.get('loggedin'):
        return redirect(url_for('login'))

    # print(session['username'])
    return render_template('index.html' , companies=companies, car_models=car_models, year=year, fuel_type=fuel_type, prediction=prediction, title="Home", reviews=reviews)
    # User is not loggedin redirect to login page
    

@app.route('/comment', methods=['POST'])
def comment():
    if request.method == 'POST':
        # name from session
        name = session['username']
        comment = request.form['comment']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO reviews VALUES (NULL, %s, %s)', (comment, name))
        mysql.connection.commit()
        flash("Thanks for your feedback!", "success")
        return redirect(url_for('home'))
        

@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    company=request.form.get('company')

    car_model=request.form.get('car_models')
    year=request.form.get('year')
    fuel_type=request.form.get('fuel_type')
    driven=request.form.get('kilo_driven')

    
    prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                              data=np.array([car_model,company,year,driven,fuel_type]).reshape(1, 5)))
    print(prediction)

    # insert to database predict value
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO prediction VALUES (NULL, %s)', (prediction))
    mysql.connection.commit()
    


    return str(np.round(prediction[0],2))


    if __name__ == '__main__':
        app.run(debug=True)