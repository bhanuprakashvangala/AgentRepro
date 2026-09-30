import sqlite3
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, g, abort

# --- Configuration ---
DATABASE = 'shortener.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-for-flashing' # Required for flash messages

# --- Database Setup ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    print("Database initialized.")

# Command to initialize the DB: flask init-db
@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    init_db()

# --- Helper Functions ---
def generate_short_code(num_chars=6):
    """Generate a unique random short code."""
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))
        db = get_db()
        if not db.execute('SELECT short_code FROM urls WHERE short_code = ?', (code,)).fetchone():
            return code

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        custom_alias = request.form['custom_alias']
        expires_in_hours = request.form.get('expires_in', type=int)

        if not original_url:
            flash('You must enter a URL to shorten!', 'error')
            return redirect(url_for('index'))

        db = get_db()
        short_code = custom_alias or generate_short_code()

        if db.execute('SELECT short_code FROM urls WHERE short_code = ?', (short_code,)).fetchone():
            flash(f"Custom alias '{short_code}' is already taken!", 'error')
            return redirect(url_for('index'))

        expires_at = None
        if expires_in_hours and expires_in_hours > 0:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        db.execute(
            'INSERT INTO urls (original_url, short_code, expires_at) VALUES (?, ?, ?)',
            (original_url, short_code, expires_at)
        )
        db.commit()

        full_short_url = request.host_url + short_code
        flash(f'Success! Your shortened URL is: <a href="{full_short_url}">{full_short_url}</a>', 'success')
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/<string:short_code>')
def redirect_to_url(short_code):
    db = get_db()
    url_data = db.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,)).fetchone()

    if url_data is None:
        return abort(404)

    # Check for expiration
    if url_data['expires_at']:
        expires_at = datetime.strptime(url_data['expires_at'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() > expires_at:
            flash(f"Link '{short_code}' has expired.", 'error')
            return render_template('404.html'), 404

    # Update click count and redirect
    db.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
    db.commit()
    return redirect(url_data['original_url'])

@app.route('/stats/<string:short_code>')
def view_stats(short_code):
    db = get_db()
    url_data = db.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,)).fetchone()
    if url_data is None:
        return abort(404)
    return render_template('stats.html', url=url_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
