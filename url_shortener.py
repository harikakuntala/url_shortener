from flask import Flask, request, redirect, jsonify, render_template
import random
import string
import sqlite3

app = Flask(__name__)
DATABASE = 'urls.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            short_url TEXT UNIQUE,
                            long_url TEXT UNIQUE)''')
        conn.commit()

# Generate short URL
def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Store URL mapping
def store_url(short_url, long_url):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO urls (short_url, long_url) VALUES (?, ?)", (short_url, long_url))
        conn.commit()

# Retrieve URL
def get_long_url(short_url):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT long_url FROM urls WHERE short_url = ?", (short_url,))
        result = cursor.fetchone()
        return result[0] if result else None

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Shorten URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get("long_url")
    
    if not long_url:
        return jsonify({"error": "Missing URL"}), 400
    
    short_url = generate_short_url()
    store_url(short_url, long_url)
    
    return jsonify({"short_url": request.host_url + short_url})

# Redirect Short URL
@app.route('/<short_url>')
def redirect_url(short_url):
    long_url = get_long_url(short_url)
    if long_url:
        return redirect(long_url)
    return jsonify({"error": "URL not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
