import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'raise_on_warnings': True,
    'autocommit': True
}

TOM_PASSWORD = os.getenv("TOM_PASSWORD")
FLAG = os.getenv("FLAG")

def get_db_connection():
    return mysql.connector.connect(**db_config)

def init_db_with_retry(retries=15, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """)
            cursor.execute("SELECT id FROM users WHERE username = %s", ("Tom",))
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("Tom", TOM_PASSWORD))
                app.logger.info("Inserted initial user 'Tom' into users table.")
            cursor.close()
            conn.close()
            return
        except Error as e:
            attempt += 1
            app.logger.warning(f"DB not ready (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
    app.logger.error("Could not connect to the database after retries. Exiting init.")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
            cursor.execute(query)
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['username'] = username
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
        except Error as e:
            flash(f'Database error: {e}', 'danger')

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', message=FLAG)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db_with_retry()
    app.run(host='0.0.0.0', port=7014)