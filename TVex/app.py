from flask import Flask, request, jsonify, send_from_directory
from plexapi.server import PlexServer
from flask_cors import CORS
import random

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/load_shows", methods=["POST"])
def load_shows():
    try:
        data = request.get_json()
        plex = PlexServer(data["plex_url"], data["plex_token"])
        section = plex.library.section(data["library"])
        shows = section.all()

        show_data = []
        for show in shows:
            thumb_path = show.thumb or show.art or ""
            thumb_url = f"{data['plex_url']}{thumb_path}?X-Plex-Token={data['plex_token']}" if thumb_path else ""
            genres = [g.tag for g in getattr(show, 'genres', [])]
            show_data.append({
                "title": show.title,
                "ratingKey": show.ratingKey,
                "thumb": thumb_path,
                "year": getattr(show, 'year', ''),
                "genres": genres
            })

        return jsonify({"success": True, "shows": show_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    try:
        data = request.get_json()
        plex = PlexServer(data["plex_url"], data["plex_token"])
        playlist_name = data["playlistName"].strip()
        selected_keys = data["selectedShows"]

        if not playlist_name:
            return jsonify({"success": False, "error": "Playlist name is required."}), 400

        add_commercials = data.get("addCommercials", False)
        commercial_library = data.get("commercialLibrary", "")
        commercial_count = int(data.get("commercialCount", 1))
        shuffle_episodes = data.get("shuffleEpisodes", False)
        create_collection = data.get("createCollection", False)
        collection_name = data.get("collectionName", "").strip()

        # Load episodes
        show_episodes = []
        for key in selected_keys:
            show = plex.fetchItem(int(key))
            try:
                episodes = sorted(show.episodes(), key=lambda e: (getattr(e, 'seasonNumber', 0), getattr(e, 'index', 0)))
                show_episodes.append(episodes)
            except:
                show_episodes.append([show])

        ordered_episodes = [ep for eps in show_episodes for ep in eps]
        if shuffle_episodes:
            random.shuffle(ordered_episodes)

        commercials = []
        if add_commercials and commercial_library:
            try:
                commercial_section = plex.library.section(commercial_library)
                commercials = commercial_section.all()
                random.shuffle(commercials)
            except Exception as ce:
                return jsonify({"success": False, "error": f"Failed to load commercials: {ce}"}), 500

        final_playlist = []
        commercial_index = 0
        total_commercials = len(commercials)
        final_playlist = []
        commercial_index = 0
        total_commercials = len(commercials)

        for ep in ordered_episodes:
            final_playlist.append(ep)
            if add_commercials and total_commercials > 0:
                count = min(commercial_count, total_commercials)
                for i in range(count):
                    final_playlist.append(commercials[commercial_index % total_commercials])
                    commercial_index += 1


        if not final_playlist:
            return jsonify({"success": False, "error": "No items found to create playlist."}), 400

        existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
        if existing:
            existing.replaceItems(final_playlist)
        else:
            plex.createPlaylist(playlist_name, items=final_playlist)

        
        # Save playlist generation script
        script_content = f"""from plexapi.server import PlexServer
import random

plex = PlexServer(\"{data['plex_url']}\", \"{data['plex_token']}\")
selected_keys = {selected_keys}
playlist_name = \"{playlist_name}\"
add_commercials = {add_commercials}
commercial_library = \"{commercial_library}\"
commercial_count = {commercial_count}
shuffle_episodes = {shuffle_episodes}

show_episodes = []
for key in selected_keys:
    show = plex.fetchItem(int(key))
    try:
        episodes = sorted(show.episodes(), key=lambda e: (getattr(e, 'seasonNumber', 0), getattr(e, 'index', 0)))
        show_episodes.append(episodes)
    except:
        show_episodes.append([show])

ordered_episodes = [ep for eps in show_episodes for ep in eps]
if shuffle_episodes:
    random.shuffle(ordered_episodes)

commercials = []
if add_commercials and commercial_library:
    try:
        commercial_section = plex.library.section(commercial_library)
        commercials = commercial_section.all()
        random.shuffle(commercials)
    except Exception as ce:
        print(\"Failed to load commercials:\", ce)

final_playlist = []
commercial_index = 0
total_commercials = len(commercials)

for ep in ordered_episodes:
    final_playlist.append(ep)
    if add_commercials and total_commercials > 0:
        count = min(commercial_count, total_commercials)
        for i in range(count):
            final_playlist.append(commercials[commercial_index % total_commercials])
            commercial_index += 1


existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
if existing:
    existing.replaceItems(final_playlist)
else:
    plex.createPlaylist(playlist_name, items=final_playlist)

print(f\"Playlist '{{playlist_name}}' created with {{len(final_playlist)}} items.\")"""

        with open("run_playlist.py", "w") as f:
            f.write(script_content)

        # Save playlist deletion script
        cleaner_script = f"""from plexapi.server import PlexServer

plex = PlexServer(\"{data['plex_url']}\", \"{data['plex_token']}\")
playlist_name = \"{playlist_name}\"

existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
if existing:
    existing.delete()
    print(f\"Playlist '{{playlist_name}}' deleted.\")
else:
    print(f\"Playlist '{{playlist_name}}' not found.\")"""

        with open("playlist_cleaner.py", "w") as f:
            f.write(cleaner_script)

        if create_collection and collection_name:
            try:
                items_for_collection = [plex.fetchItem(int(key)) for key in selected_keys]
                lib_section = plex.library.section(data["library"])
                existing_collection = next((c for c in lib_section.collections() if c.title == collection_name), None)
                if existing_collection:
                    existing_collection.replaceItems(items_for_collection)
                else:
                    lib_section.createCollection(collection_name, items_for_collection)
            except Exception as ce:
                print("Failed to create collection:", ce)

        return jsonify({"success": True, "count": len(final_playlist)})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/create_collection", methods=["POST"])
def create_collection():
    try:
        data = request.get_json()
        plex = PlexServer(data["plex_url"], data["plex_token"])
        selected_keys = data.get("selectedShows", [])
        collection_name = data.get("collectionName", "").strip()
        library_name = data.get("library", "").strip()

        if not collection_name:
            return jsonify({"success": False, "error": "Collection name is required."}), 400

        items = [plex.fetchItem(int(key)) for key in selected_keys]
        section = plex.library.section(library_name)

        existing = next((c for c in section.collections() if c.title == collection_name), None)
        if existing:
            existing.replaceItems(items)
        else:
            section.createCollection(collection_name, items)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
