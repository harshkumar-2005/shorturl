from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import string
import sqlite3




app = Flask(__name__)


def create_tables():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE
        )
    """)
    connection.commit()
    connection.close()

# Call this function when the app starts
create_tables()


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def save_url(original_url):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    while True:
        short_code = generate_short_code()
        cursor.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,))
        if not cursor.fetchone():
            break

    cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
    conn.commit()
    conn.close()
    return short_code

def get_original_url(short_code):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["original_url"]
        short_code = save_url(original_url)
        return render_template("shortened.html", short_url=request.host_url + short_code)
    return render_template("index.html")

@app.route("/<short_code>")
def redirect_url(short_code):
    original_url = get_original_url(short_code)
    if original_url:
        return redirect(original_url)
    return "URL not found", 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
