import os
from flask import Flask, request, Response
import requests
import random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 Chrome/87.0.4280.101 Mobile Safari/537.36"
]

@app.route('/')
def home():
    return '✅ HLS Proxy is running!'

@app.route('/bypass')
def bypass():
    url = request.args.get('url')
    if not url:
        return "❌ Missing 'url' parameter", 400

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://re.fredflix.fun/",
        "Origin": "https://re.fredflix.fun"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()

        content_type = r.headers.get('Content-Type', 'application/vnd.apple.mpegurl')
        return Response(r.content, content_type=content_type)

    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}", 500
    except requests.exceptions.ConnectionError as errc:
        return f"Connection Error: {errc}", 500
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}", 500
    except requests.exceptions.RequestException as err:
        return f"Error: {err}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
