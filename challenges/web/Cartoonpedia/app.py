from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD",),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "autocommit": True,
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/", methods=["GET", "POST"])
def index():
    cartoons = []
    error_message = None

    if request.method == "POST":
        search_query = request.form.get("search", "").strip()
        try:
            conn = get_conn()
            cursor = conn.cursor(dictionary=True)

            if search_query:
                cursor.execute(f"SELECT * FROM cartoons WHERE name LIKE '%{search_query}%'")
                cartoons = cursor.fetchall()
            else:
                error_message = "Please enter a cartoon name to search."

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            error_message = f"Database error: {err}"

    return render_template("index.html", cartoons=cartoons, error_message=error_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)