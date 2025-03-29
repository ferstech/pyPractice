from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import requests
from urllib.parse import quote_plus
from functools import lru_cache

app = Flask(__name__)

songs = []

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎵 AI Jukebox</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            background: #f7f7fa;
            margin: 0;
            padding: 0;
        }
        h1 {
            text-align: center;
            color: #2d2d2d;
            margin-top: 30px;
            font-weight: 700;
        }
        #addForm {
            max-width: 500px;
            margin: 30px auto 10px auto;
            background: #fff;
            padding: 24px 32px 32px 32px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            position: relative;
        }
        #addForm input[type="text"] {
            width: 70%;
            padding: 10px;
            border: 1px solid #bbb;
            border-radius: 6px;
            font-size: 1em;
            margin-right: 8px;
        }
        #addForm button {
            padding: 10px 18px;
            background: #4f8cff;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.2s;
        }
        #addForm button:hover {
            background: #2563eb;
        }
        #suggestions {
            border: 1px solid #bbb;
            border-top: none;
            display: none;
            position: absolute;
            background: #fff;
            width: 70%;
            left: 0;
            top: 60px;
            z-index: 10;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            max-height: 220px;
            overflow-y: auto;
        }
        #suggestions div {
            padding: 10px 14px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.15s;
        }
        #suggestions div:last-child {
            border-bottom: none;
        }
        #suggestions div:hover {
            background: #f1f5ff;
        }
        ul {
            max-width: 500px;
            margin: 30px auto;
            padding: 0;
            list-style: none;
        }
        li {
            background: #fff;
            margin-bottom: 12px;
            padding: 16px 20px;
            border-radius: 10px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        li a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }
        li a:hover {
            text-decoration: underline;
        }
        .votes {
            background: #e0e7ff;
            color: #3730a3;
            border-radius: 6px;
            padding: 4px 10px;
            margin-right: 10px;
            font-weight: 700;
        }
        .upvote-form {
            display: inline;
        }
        .upvote-form button {
            background: #22c55e;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 1em;
            margin-left: 8px;
            transition: background 0.2s;
        }
        .upvote-form button:hover {
            background: #15803d;
        }
        @media (max-width: 600px) {
            #addForm, ul {
                max-width: 98vw;
                padding: 10px;
            }
            #addForm input[type="text"], #suggestions {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <h1>🎵 AI Jukebox</h1>
    <p style="text-align:center;color:#555;margin-bottom:10px;">
    Add your favorite songs! Type at least 5 letters to search. You can upvote songs and see who added them.
</p>

    <form id="addForm" action="/add" method="post" autocomplete="off">
        <input type="text" name="title" id="title" placeholder="Search YouTube Music" required>
        <input type="hidden" name="url" id="url">
        <input type="text" name="added_by" id="added_by" placeholder="Your name (optional)" style="margin-top:8px;width:70%;padding:10px;border:1px solid #bbb;border-radius:6px;font-size:1em;">
        <button type="submit">Add Song</button>
        <div id="suggestions"></div>
    </form>

    <ul>
        {% for song in songs %}
            <li>
                <span>
                    <a href="{{ song.url }}" target="_blank">{{ song.title }}</a>
                    {% if song.added_by %}
                        <span style="color:#888;font-size:0.95em;">(added by {{ song.added_by }})</span>
                    {% endif %}
                    <span class="votes">Votes: {{ song.votes }}</span>
                </span>
                <form class="upvote-form" action="/upvote/{{ loop.index0 }}" method="post">
                    <button type="submit">👍 Upvote</button>
                </form>
                {% if request.args.get('host') == '1' %}
                <form class="remove-form" action="/remove/{{ loop.index0 }}" method="post" style="display:inline;">
                    <button type="submit" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:1em;margin-left:8px;">🗑 Remove</button>
                </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>

<div id="player-container" style="max-width:500px;margin:30px auto;">
    <div id="player"></div>
</div>
<div id="now-playing" style="text-align:center;margin:20px 0;font-size:1.2em;font-weight:500;">
    Now Playing: <span id="now-playing-title"></span>
</div>
<script src="https://www.youtube.com/iframe_api"></script>

<script>
let songQueue = {{ songs|tojson }};
let currentSongIndex = 0;
let player;

function onYouTubeIframeAPIReady() {
    if (songQueue.length > 0) {
        loadAndPlay(songQueue[0].url);
    }
}

function loadAndPlay(url) {
    const videoId = url.split('v=')[1];
    document.getElementById("now-playing-title").textContent = songQueue[currentSongIndex]?.title || "";
    if (!player) {
        player = new YT.Player('player', {
            height: '300',
            width: '100%',
            videoId: videoId,
            events: {
                'onStateChange': onPlayerStateChange
            }
        });
    } else {
        player.loadVideoById(videoId);
    }
}

function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.ENDED) {
        currentSongIndex++;
        if (currentSongIndex < songQueue.length) {
            loadAndPlay(songQueue[currentSongIndex].url);
        } else {
            // Queue is empty, fetch similar songs
            fetch('/ai_suggest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({songs: songQueue})
            })
            .then(res => res.json())
            .then(data => {
                if (data.length > 0) {
                    songQueue = data;
                    currentSongIndex = 0;
                    loadAndPlay(songQueue[0].url);
                }
            });
        }
    }
}
</script>

<script>
let debounceTimeout = null;
let lastQuery = "";
let lastResults = [];
document.getElementById("title").addEventListener("input", function() {
    clearTimeout(debounceTimeout);
    const query = this.value;
    const container = document.getElementById("suggestions");
    if (query.length < 3) {
        container.style.display = "none";
        return;
    }
    debounceTimeout = setTimeout(async () => {
        if (query === lastQuery) {
            showSuggestions(lastResults, container);
            return;
        }
        const res = await fetch("/suggest?q=" + encodeURIComponent(query));
        const suggestions = await res.json();
        lastQuery = query;
        lastResults = suggestions;
        showSuggestions(suggestions, container);
    }, 600);
});
function showSuggestions(suggestions, container) {
    container.innerHTML = "";
    if (suggestions.length === 0) {
        container.style.display = "none";
        return;
    }
    container.style.display = "block";
    suggestions.forEach(item => {
        const div = document.createElement("div");
        div.innerHTML = `<strong>${item.title}</strong><br><small>${item.channel}</small>`;
        div.onclick = () => {
            document.getElementById("title").value = item.title;
            document.getElementById("url").value = item.url;
            container.style.display = "none";
            window.open(item.url, "_blank");
        };
        container.appendChild(div);
    });
}
document.addEventListener("click", function(e) {
    const container = document.getElementById("suggestions");
    if (!container.contains(e.target) && e.target.id !== "title") {
        container.style.display = "none";
    }
});
document.getElementById("addForm").addEventListener("submit", function() {
    this.querySelector("button[type='submit']").disabled = true;
});
</script>

</body>
</html>
'''

@app.route('/')
def index():
    sorted_songs = sorted(songs, key=lambda x: x['votes'], reverse=True)
    return render_template_string(HTML_TEMPLATE, songs=sorted_songs)

@app.route('/add', methods=['POST'])
def add_song():
    title = request.form['title']
    url = request.form['url']
    added_by = request.form.get('added_by', '').strip()
    # Limit: max 3 songs per name
    if added_by:
        user_songs = [s for s in songs if s.get('added_by', '') == added_by]
        if len(user_songs) >= 3:
            return redirect(url_for('index'))
    if any(song['url'] == url for song in songs):
        return redirect(url_for('index'))
    songs.append({'title': title, 'url': url, 'votes': 0, 'added_by': added_by})
    return redirect(url_for('index'))

@app.route('/upvote/<int:song_index>', methods=['POST'])
def upvote_song(song_index):
    songs[song_index]['votes'] += 1
    return redirect(url_for('index'))

@app.route('/remove/<int:song_index>', methods=['POST'])
def remove_song(song_index):
    if 0 <= song_index < len(songs):
        songs.pop(song_index)
    return redirect(url_for('index', host=1))

@lru_cache(maxsize=256)
def cached_youtube_results(query):
    return tuple(get_youtube_results(query))

@app.route('/suggest')
def suggest():
    query = request.args.get("q", "")
    results = cached_youtube_results(query)
    return jsonify(list(results))

@app.route('/ai_suggest', methods=['POST'])
def ai_suggest():
    data = request.get_json()
    if not data['songs']:
        return jsonify([])
    last_song = data['songs'][-1]
    # Use the last song's title as a query for similar songs
    results = get_youtube_results(last_song['title'])
    return jsonify(results)

YOUTUBE_API_KEY = 'key'  # Or hardcode for dev

def get_youtube_results(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        results.append({
            "title": title,
            "channel": channel,
            "url": video_url
        })

    return results

if __name__ == '__main__':
    app.run(debug=True)
