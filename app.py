import os
import psycopg2
import csv
from flask import Flask, render_template, request, Response

app = Flask(__name__)

DATABASE_URL = os.environ.get('postgresql://shopfi_db_user:KkEiHyzjqO9Pz5H83nNwj0fQhjdMZzbm@dpg-d1vmar2dbo4c73flg0k0-a.oregon-postgres.render.com/shopfi_db')


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


# Create table if not exists
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT
            );
        """)
    conn.commit()


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


@app.route('/download', methods=['GET'])
def download():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM users;")
            rows = cur.fetchall()

    def generate():
        data = csv.writer(Response())
        yield 'name\n'  # CSV Header
        for row in rows:
            yield f"{row[0]}\n"

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=names.csv"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
