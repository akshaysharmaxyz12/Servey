# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import *

app = Flask(__name__)
app.config['MYSQL_HOST'] = DATABASE_HOST
app.config['MYSQL_USER'] = DATABASE_USER
app.config['MYSQL_PASSWORD'] = DATABASE_PASSWORD
app.config['MYSQL_DB'] = DATABASE_NAME
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

mysql = MySQL(app)

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        # Fetch the current question ID from the URL or default to the first question
        question_id = int(request.args.get('question_id', 1))
        # Fetch the question from the database based on the current question ID
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cur.fetchone()
        if question:
            # Fetch options for the current question
            cur.execute("SELECT * FROM options WHERE question_id = %s", (question_id,))
            options = cur.fetchall()
            cur.close()
            return render_template('survey.html', question=question, options=options)
        else:
            # If there are no more questions, display a completion message
            return "Survey completed successfully"
    else:
        return redirect(url_for('register'))

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Retrieve question and option IDs from the form submission
        question_id = int(request.form['question_id'])
        option_id = int(request.form['option_id'])
        
        # Retrieve the user ID from the session
        user_id = session['user_id']

        # Insert the response into the database table named after the user ID
        cur = mysql.connection.cursor()
        table_name = f"user_{user_id}"  # Name the table after the user ID
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, question_id INT, option_id INT)")
        cur.execute(f"INSERT INTO {table_name} (question_id, option_id) VALUES (%s, %s)", (question_id, option_id))
        mysql.connection.commit()
        cur.close()

        # Determine the next question ID based on the current question and selected option
        next_question_id = None  # Initialize next question ID

        if question_id == 1:
            if option_id in [1, 2, 3, 4]:
                next_question_id = option_id + 1
        elif question_id == 2:
            if option_id in [1, 2, 3, 4]:
                next_question_id = option_id + 3
        elif question_id == 3:
            if option_id in [1, 2, 3, 4]:
                next_question_id = option_id + 4
        elif question_id == 4:
            if option_id in [1, 2, 3, 4]:
                next_question_id = option_id + 5
        elif question_id == 5:
            if option_id in [1, 2, 3, 4]:
                next_question_id = 6
        else:
            next_question_id = None  # End survey if all questions are completed

        # Redirect to the next question or survey completion page
        if next_question_id:
            return redirect(url_for('index', question_id=next_question_id))
        else:
            return "Survey completed successfully"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve registration data from the form submission
        username = request.form['username']
        email = request.form['email']

        # Insert the new user into the database and store the user ID in session
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        mysql.connection.commit()
        user_id = cur.lastrowid  # Get the ID of the newly inserted user
        session['user_id'] = user_id  # Store the user ID in the session
        cur.close()
        
        # Proceed to the survey
        return redirect(url_for('index'))

    # Render the registration form
    return render_template('register.html')
