import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, send_file

app = Flask(__name__)
DB_PATH = 'database.db'

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (name TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    username = None
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name) VALUES (?)', (username,))
            conn.commit()
            conn.close()
    return render_template('index.html', username=username)


@app.route('/download', methods=['GET'])
def download():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name FROM users", conn)
    file_path = 'names.csv'
    df.to_csv(file_path, index=False)
    conn.close()
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
