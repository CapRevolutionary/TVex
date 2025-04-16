# 🎬 TVex: Custom Plex Playlist Creator

TVex is a web-based tool that lets you create smart, dynamic Plex playlists with optional commercials and bumpers — like a personal curated TV channel! Built with Flask and the `plexapi`, it's your nostalgic Saturday morning lineup on demand.

![TVex UI](https://i.imgur.com/HkPUNyB.png)

---

## ⚙️ Features

- ✅ Web interface for selecting Plex shows from multiple libraries
- ✅ Create shuffled or ordered playlists
- ✅ Inject commercials and/or bumpers into playlists
- ✅ Optionally create a matching Plex collection
- ✅ Generates reusable playlist scripts (`run_playlist.py` & `playlist_cleaner.py`)
- ✅ Auto-pulls posters and lets you select shows by clicking thumbnails
- ✅ "Remember Me" feature for Plex URL & token

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Plex server with API access token
- TV Shows in Plex libraries
- Optional: Commercials and Bumpers libraries in Plex

### Installation

1. Download The Code 

  From Top Of Page Download ZIP
  
2. Start the app:

   Open The app.py

3. Open your browser and visit:  

   http://localhost:5000
 

---

## 🧠 Usage

1. Enter your **Plex URL** and **Plex Token**
2. Type your **Library name** (e.g., `TV Shows`)
3. Click `Load Shows` to see thumbnails
4. Select shows you want in the playlist
5. Choose options:
   - Playlist name
   - Add Commercials / Bumps
   - Shuffle Episodes
   - Create Collection
6. Click `Create Playlist`  
   You can also generate collections independently with `Create Collection`

### 🛠 Scripts Generated

- **`run_playlist.py - Rename This Every Playlist`**  
  Recreates the same playlist programmatically.
- **`playlist_cleaner.py - Rename This Every Playlist`**  
  Deletes the generated playlist.

---

## 📁 File Structure

```
tvex/
├── app.py                # Flask backend
├── index.html            # Frontend UI
├── script.js             # Frontend logic
├── run_playlist.py       # Generated playlist script
├── playlist_cleaner.py   # Playlist deletion script
├── requirements.txt      # Dependencies
```

---

## 🧪 Example

Example: Create a Toonami-style playlist with shuffled anime episodes, bumpers, and commercials per episode.

```bash
# Result: Playlist with mixed ads, anime, and nostalgic vibes!
```

---


## 🛡️ Disclaimer

This tool uses your local Plex server API — make sure not to expose your token publicly. Always secure your server URL And ID Are Stored Locally.

---

## 🧑‍💻 Author

Made with ❤️ for Plex fans by [CapRevolutionary](https://github.com/CapRevolutionary)
