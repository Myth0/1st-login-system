from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

#load_dotenv()  # <-- this reads your .env file

app = Flask(__name__)

DB_STRING = os.getenv("DB_STRING")
if not DB_STRING:
    raise ValueError("DB_STRING is not set! Check your .env file.")

def get_conn():
    return psycopg2.connect(DB_STRING, cursor_factory=RealDictCursor)

# Initialize database
def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    conn.close()
    return render_template("index.html", users=users)

@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        pass
    finally:
        conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=False)