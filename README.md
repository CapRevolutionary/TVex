TVex is a simple web app that lets you build custom Plex playlists using your own TV shows, with optional commercials, bumps, and idents for an authentic TV-style experience.

---

## 🔧 How to Use

### 1. **Install the Requirements**

Make sure you have Python 3 installed, then run:

```bash
pip install -r requirements.txt
```

---

### 2. **Start the App**

Launch the web interface with:

```bash
python app.py
```

This will open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

### 3. **Connect to Your Plex Server**

- Enter your **Plex server URL** (e.g., `http://localhost:32400`)
- Enter your **Plex token**

---

### 4. **(Optional) Set Up Commercials, Bumps, and Idents**

Before loading shows, you can configure additional media to insert around episodes:

- **Commercials**
  - Enable the checkbox for **Add Commercials**
  - Enter the **Commercials Library Name**
  - (Optional) Choose a **Collection** from that library
  - Select how many commercials per episode (e.g., 1–6)

- **Bumps**
  - Enable **Add Bumps**
  - Enter the **Bumps Library Name**
  - (Optional) Choose a **Collection**
  - Choose how many bumps per episode

- **Idents**
  - Enable **Add Idents**
  - Enter the **Idents Library Name**
  - (Optional) Choose a **Collection**
  - DONT CHANGE IDENTS FROM 1
  - MAKE SURE TO ENTER YOUR COMMERCIAL,BUMPS AND IDENTS INFORMATION BEFORE LOADING SHOWS

You can also:
- Enable **Shuffle Episodes**
- Enable **Create Collection** and enter a name to group the playlist content in Plex

---

### 5. **Select Shows and Episodes**

- Enter the name of your **TV Library**
- Click **Load Shows**
- Select full shows by clicking posters, or choose individual episodes using dropdowns

---

### 6. **Create the Playlist**

- Enter a **Playlist Name**
- Click **Create Playlist**
- A success message will confirm if the playlist was created in your Plex server

---

### 7. **Use the Generated Scripts**

After a playlist is created, two Python scripts are automatically saved:

#### `run_playlist.py`

- Recreates the playlist with the same shows, episodes, and settings
- Run it anytime with:

```bash
python run_playlist.py
```

#### `playlist_cleaner.py`

- Deletes the generated playlist from your Plex server
- Run it with:

```bash
python playlist_cleaner.py
```

REMEMBER ME IS BUGGED ATM 
