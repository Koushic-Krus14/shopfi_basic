import os
import psycopg2
import pandas as pd
from flask import Flask, render_template, request, send_file
from io import StringIO

app = Flask(__name__)

# Get connection string from Render Environment Variable
DATABASE_URL = os.environ.get('postgresql://shopfi_db_user:KkEiHyzjqO9Pz5H83nNwj0fQhjdMZzbm@dpg-d1vmar2dbo4c73flg0k0-a.oregon-postgres.render.com/shopfi_db')

# Function to get DB connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Create the users table if it doesn't exist
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT
            );
        """)
    conn.commit()

# Home Route: Accept and store username
@app.route('/', methods=['GET', 'POST'])
def home():
    username = None
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('INSERT INTO users (name) VALUES (%s)', (username,))
                conn.commit()
    return render_template('index.html', username=username)

# Download CSV of usernames
@app.route('/download', methods=['GET'])
def download():
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT name FROM users", conn)

    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='names.csv')

# Run the app on Render (0.0.0.0 with PORT from environment)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
