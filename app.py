from flask import Flask, request, Response
import requests
import re
import random

app = Flask(__name__)

# Random User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
]

HEADERS = lambda: {
    "User-Agent": random.choice(USER_AGENTS),
    "Origin": "https://re.fredflix.fun",
    "Referer": "https://re.fredflix.fun/",
}

@app.route('/bypass')
def bypass():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    r = requests.get(url, headers=HEADERS())
    m3u8_match = re.search(r"source:\s*['\"](https.*?playlist\.m3u8[^'\"]*)['\"]", r.text)
    if not m3u8_match:
        return "No .m3u8 found", 404

    m3u8_url = m3u8_match.group(1)
    r2 = requests.get(m3u8_url, headers=HEADERS())
    if r2.status_code != 200:
        return "Failed to fetch .m3u8", 500

    base = m3u8_url.split('?')[0]
    query = m3u8_url.split('?')[1] if '?' in m3u8_url else ""

    lines = []
    for line in r2.text.splitlines():
        if line.strip().startswith('#') or line.strip() == "":
            lines.append(line)
        elif "segment=" in line:
            segment_id = re.search(r"segment=([\w\d]+)", line)
            if segment_id:
                full_url = f"/ts?base={base}&seg={segment_id.group(1)}&{query}"
                lines.append(full_url)
            else:
                lines.append(line)
        else:
            lines.append(line)

    fixed_m3u8 = '\n'.join(lines)
    return Response(fixed_m3u8, content_type='application/vnd.apple.mpegurl')


@app.route('/ts')
def ts_proxy():
    base = request.args.get('base')
    seg = request.args.get('seg')
    query = request.query_string.decode().split("&", 2)[2] if "&" in request.query_string.decode() else ""

    if not base or not seg:
        return "Missing parameters", 400

    target_url = f"{base}?segment={seg}"
    if query:
        target_url += f"&{query}"

    resp = requests.get(target_url, headers=HEADERS(), stream=True)
    if resp.status_code != 200:
        return f"Failed to fetch TS: {resp.status_code}", 502

    return Response(resp.iter_content(chunk_size=4096),
                    content_type=resp.headers.get('Content-Type', 'video/MP2T'))

if __name__ == '__main__':
    app.run(debug=True)
