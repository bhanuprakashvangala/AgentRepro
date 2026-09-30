from flask import Flask, request, redirect, render_template_string, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import string
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BASE_URL'] = 'http://localhost:5000'

db = SQLAlchemy(app)

# Database Models
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    custom_alias = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    clicks = db.relationship('Click', backref='url', lazy=True, cascade='all, delete-orphan')

    def is_expired(self):
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def total_clicks(self):
        return len(self.clicks)


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(256))
    referer = db.Column(db.String(512))


# Helper Functions
def generate_short_code(length=6):
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        if not URL.query.filter_by(short_code=short_code).first():
            return short_code


def is_valid_custom_alias(alias):
    """Validate custom alias"""
    if len(alias) < 3 or len(alias) > 20:
        return False
    # Only allow alphanumeric characters, hyphens, and underscores
    allowed = set(string.ascii_letters + string.digits + '-_')
    return all(c in allowed for c in alias)


# Routes
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Create a shortened URL"""
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    original_url = data['url']
    custom_alias = data.get('custom_alias', '').strip()
    expiration_hours = data.get('expiration_hours')

    # Validate URL
    if not original_url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL format. Must start with http:// or https://'}), 400

    # Handle custom alias
    if custom_alias:
        if not is_valid_custom_alias(custom_alias):
            return jsonify({'error': 'Invalid custom alias. Must be 3-20 characters (letters, numbers, hyphens, underscores)'}), 400

        if URL.query.filter_by(short_code=custom_alias).first():
            return jsonify({'error': 'Custom alias already taken'}), 400

        short_code = custom_alias
        is_custom = True
    else:
        short_code = generate_short_code()
        is_custom = False

    # Handle expiration
    expires_at = None
    if expiration_hours:
        try:
            hours = int(expiration_hours)
            if hours > 0:
                expires_at = datetime.utcnow() + timedelta(hours=hours)
        except ValueError:
            return jsonify({'error': 'Invalid expiration time'}), 400

    # Create URL record
    url_record = URL(
        original_url=original_url,
        short_code=short_code,
        custom_alias=is_custom,
        expires_at=expires_at
    )

    db.session.add(url_record)
    db.session.commit()

    short_url = f"{app.config['BASE_URL']}/{short_code}"

    return jsonify({
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url,
        'created_at': url_record.created_at.isoformat(),
        'expires_at': expires_at.isoformat() if expires_at else None
    }), 201


@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a shortened URL"""
    url_record = URL.query.filter_by(short_code=short_code).first()

    if not url_record:
        return jsonify({'error': 'URL not found'}), 404

    # Get click statistics
    clicks = Click.query.filter_by(url_id=url_record.id).order_by(Click.clicked_at.desc()).all()

    # Aggregate stats
    total_clicks = len(clicks)
    clicks_by_date = {}

    for click in clicks:
        date_key = click.clicked_at.strftime('%Y-%m-%d')
        clicks_by_date[date_key] = clicks_by_date.get(date_key, 0) + 1

    recent_clicks = [{
        'timestamp': click.clicked_at.isoformat(),
        'ip_address': click.ip_address,
        'user_agent': click.user_agent,
        'referer': click.referer
    } for click in clicks[:20]]  # Last 20 clicks

    return jsonify({
        'short_code': short_code,
        'original_url': url_record.original_url,
        'created_at': url_record.created_at.isoformat(),
        'expires_at': url_record.expires_at.isoformat() if url_record.expires_at else None,
        'is_expired': url_record.is_expired(),
        'custom_alias': url_record.custom_alias,
        'total_clicks': total_clicks,
        'clicks_by_date': clicks_by_date,
        'recent_clicks': recent_clicks
    })


@app.route('/api/urls')
def list_urls():
    """List all shortened URLs"""
    urls = URL.query.order_by(URL.created_at.desc()).all()

    return jsonify([{
        'short_code': url.short_code,
        'original_url': url.original_url,
        'created_at': url.created_at.isoformat(),
        'expires_at': url.expires_at.isoformat() if url.expires_at else None,
        'is_expired': url.is_expired(),
        'total_clicks': url.total_clicks(),
        'custom_alias': url.custom_alias
    } for url in urls])


@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    """Delete a shortened URL"""
    url_record = URL.query.filter_by(short_code=short_code).first()

    if not url_record:
        return jsonify({'error': 'URL not found'}), 404

    db.session.delete(url_record)
    db.session.commit()

    return jsonify({'message': 'URL deleted successfully'})


@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to the original URL"""
    url_record = URL.query.filter_by(short_code=short_code).first()

    if not url_record:
        return render_template_string(ERROR_HTML, message='URL not found'), 404

    if url_record.is_expired():
        return render_template_string(ERROR_HTML, message='This URL has expired'), 410

    # Record the click
    click = Click(
        url_id=url_record.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:256],
        referer=request.headers.get('Referer', '')[:512]
    )
    db.session.add(click)
    db.session.commit()

    return redirect(url_record.original_url)


# HTML Templates
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .help-text {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f0f8ff;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result h3 {
            color: #333;
            margin-bottom: 10px;
        }
        .short-url {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .short-url input {
            flex: 1;
        }
        .copy-btn {
            padding: 10px 20px;
            width: auto;
            background: #4CAF50;
        }
        .stats-btn {
            padding: 10px 20px;
            width: auto;
            background: #2196F3;
            margin-top: 10px;
        }
        .error {
            background: #ffe0e0;
            border-left-color: #f44336;
            color: #c00;
        }
        .url-list {
            margin-top: 40px;
        }
        .url-item {
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .url-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        .url-item-code {
            font-weight: 600;
            color: #667eea;
        }
        .url-item-clicks {
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        .url-item-original {
            font-size: 14px;
            color: #666;
            word-break: break-all;
        }
        .url-item-meta {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .expired {
            border-left-color: #f44336;
        }
        .expired .url-item-code {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 URL Shortener</h1>
        <p class="subtitle">Create short, memorable links with custom aliases</p>

        <form id="shortenForm">
            <div class="form-group">
                <label for="url">Original URL *</label>
                <input type="text" id="url" placeholder="https://example.com/very/long/url" required>
            </div>

            <div class="form-group">
                <label for="customAlias">Custom Alias (optional)</label>
                <input type="text" id="customAlias" placeholder="my-custom-link">
                <div class="help-text">3-20 characters. Letters, numbers, hyphens, and underscores only.</div>
            </div>

            <div class="form-group">
                <label for="expiration">Expiration (hours, optional)</label>
                <input type="number" id="expiration" placeholder="24" min="1">
                <div class="help-text">Leave empty for no expiration.</div>
            </div>

            <button type="submit">Shorten URL</button>
        </form>

        <div id="result" class="result">
            <h3>✅ Success!</h3>
            <div class="short-url">
                <input type="text" id="shortUrl" readonly>
                <button class="copy-btn" onclick="copyUrl()">Copy</button>
            </div>
            <button class="stats-btn" onclick="viewStats()">View Statistics</button>
        </div>

        <div class="url-list">
            <h2>Recent URLs</h2>
            <div id="urlList"></div>
        </div>
    </div>

    <script>
        let currentShortCode = '';

        document.getElementById('shortenForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const url = document.getElementById('url').value;
            const customAlias = document.getElementById('customAlias').value;
            const expiration = document.getElementById('expiration').value;

            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: url,
                        custom_alias: customAlias,
                        expiration_hours: expiration
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    document.getElementById('shortUrl').value = data.short_url;
                    currentShortCode = data.short_code;
                    const result = document.getElementById('result');
                    result.className = 'result show';
                    loadUrls();
                } else {
                    const result = document.getElementById('result');
                    result.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
                    result.className = 'result show error';
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });

        function copyUrl() {
            const input = document.getElementById('shortUrl');
            input.select();
            document.execCommand('copy');
            alert('Copied to clipboard!');
        }

        function viewStats() {
            window.open(`/api/stats/${currentShortCode}`, '_blank');
        }

        async function loadUrls() {
            try {
                const response = await fetch('/api/urls');
                const urls = await response.json();

                const urlList = document.getElementById('urlList');
                if (urls.length === 0) {
                    urlList.innerHTML = '<p style="color: #999;">No URLs yet. Create one above!</p>';
                    return;
                }

                urlList.innerHTML = urls.slice(0, 10).map(url => `
                    <div class="url-item ${url.is_expired ? 'expired' : ''}">
                        <div class="url-item-header">
                            <span class="url-item-code">${url.short_code}${url.custom_alias ? ' (custom)' : ''}</span>
                            <span class="url-item-clicks">${url.total_clicks} clicks</span>
                        </div>
                        <div class="url-item-original">${url.original_url}</div>
                        <div class="url-item-meta">
                            Created: ${new Date(url.created_at).toLocaleString()}
                            ${url.expires_at ? `| Expires: ${new Date(url.expires_at).toLocaleString()}` : ''}
                            ${url.is_expired ? ' | <strong style="color: #f44336;">EXPIRED</strong>' : ''}
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading URLs:', error);
            }
        }

        // Load URLs on page load
        loadUrls();

        // Refresh URL list every 30 seconds
        setInterval(loadUrls, 30000);
    </script>
</body>
</html>
'''

ERROR_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .error-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #f44336;
            font-size: 48px;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            font-size: 18px;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="error-box">
        <h1>⚠️</h1>
        <p>{{ message }}</p>
        <a href="/">Go Home</a>
    </div>
</body>
</html>
'''


# Initialize database
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
