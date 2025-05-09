
from flask import Flask, request, jsonify, send_from_directory
from plexapi.server import PlexServer
from flask_cors import CORS
import random
import os

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
            show_data.append({
                "title": show.title,
                "ratingKey": show.ratingKey,
                "thumb": thumb_path,
                "year": getattr(show, 'year', ''),
                "genres": [g.tag for g in getattr(show, 'genres', [])]
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

        if not playlist_name:
            return jsonify({"success": False, "error": "Playlist name is required."}), 400

        selected_episodes = data.get("selectedEpisodes", [])
        ordered_episodes = []

        if selected_episodes:
            for ep in selected_episodes:
                show = plex.fetchItem(int(ep['ratingKey']))
                try:
                    season = next(s for s in show.seasons() if s.index == ep['season'])
                    episode = next(e for e in season.episodes() if e.index == ep['episode'])
                    ordered_episodes.append(episode)
                except Exception:
                    pass
        else:
            selected_keys = data.get("selectedShows", [])
            show_episodes = []
            for key in selected_keys:
                show = plex.fetchItem(int(key))
                try:
                    episodes = sorted(show.episodes(), key=lambda e: (getattr(e, 'seasonNumber', 0), getattr(e, 'index', 0)))
                    show_episodes.append(episodes)
                except:
                    show_episodes.append([show])
            ordered_episodes = [ep for eps in show_episodes for ep in eps]

        add_commercials = data.get("addCommercials", False)
        commercial_library = data.get("commercialLibrary", "")
        commercial_collection = data.get("commercialCollection", "")
        commercial_count = int(data.get("commercialCount", 1))

        add_bumps = data.get("addBumps", False)
        bump_library = data.get("bumpLibrary", "")
        bump_collection = data.get("bumpCollection", "")
        bump_count = int(data.get("bumpCount", 1))

        add_idents = data.get("addIdents", False)
        ident_library = data.get("identLibrary", "")
        ident_collection = data.get("identCollection", "")
        ident_count = int(data.get("identCount", 1))

        shuffle_episodes = data.get("shuffleEpisodes", False)

        if shuffle_episodes:
            random.shuffle(ordered_episodes)

        commercials = []
        if add_commercials and commercial_library:
            try:
                commercial_section = plex.library.section(commercial_library)
                if commercial_collection:
                    collection = next((c for c in commercial_section.collections() if c.title == commercial_collection), None)
                    if collection:
                        commercials = collection.items()
                    else:
                        return jsonify({"success": False, "error": f"Collection '{commercial_collection}' not found."}), 500
                else:
                    commercials = commercial_section.all()
                random.shuffle(commercials)
            except Exception as ce:
                print(f"Failed to load commercials: {ce}")

        bumps = []
        if add_bumps and bump_library:
            try:
                bump_section = plex.library.section(bump_library)
                if bump_collection:
                    collection = next((c for c in bump_section.collections() if c.title == bump_collection), None)
                    if collection:
                        bumps = collection.items()
                    else:
                        return jsonify({"success": False, "error": f"Collection '{bump_collection}' not found."}), 500
                else:
                    bumps = bump_section.all()
                random.shuffle(bumps)
            except Exception as be:
                print(f"Failed to load bumps: {be}")

        idents = []
        if add_idents and ident_library:
            try:
                ident_section = plex.library.section(ident_library)
                if ident_collection:
                    collection = next((c for c in ident_section.collections() if c.title == ident_collection), None)
                    if collection:
                        idents = collection.items()
                    else:
                        return jsonify({"success": False, "error": f"Collection '{ident_collection}' not found."}), 500
                else:
                    idents = ident_section.all()
                random.shuffle(idents)
            except Exception as ie:
                print(f"Failed to load idents: {ie}")

        final_playlist = []
        commercial_index = 0
        bump_index = 0
        ident_index = 0
        total_commercials = len(commercials)
        total_bumps = len(bumps)
        total_idents = len(idents)

        for ep in ordered_episodes:
            # Insert ident(s) BEFORE the episode
            if add_idents and total_idents > 0:
                for _ in range(min(ident_count, total_idents)):
                    final_playlist.append(idents[ident_index % total_idents])
                    ident_index += 1

            # Insert episode
            final_playlist.append(ep)

            # Insert ident(s) AFTER the episode
            if add_idents and total_idents > 0:
                for _ in range(min(ident_count, total_idents)):
                    final_playlist.append(idents[ident_index % total_idents])
                    ident_index += 1

            # Prepare bumps/commercials combined separately
            combined_ads = []
            if add_commercials and total_commercials > 0:
                for _ in range(min(commercial_count, total_commercials)):
                    combined_ads.append(commercials[commercial_index % total_commercials])
                    commercial_index += 1
            if add_bumps and total_bumps > 0:
                for _ in range(min(bump_count, total_bumps)):
                    combined_ads.append(bumps[bump_index % total_bumps])
                    bump_index += 1

            random.shuffle(combined_ads)
            final_playlist.extend(combined_ads)

        if not final_playlist:
            return jsonify({"success": False, "error": "Final playlist empty."}), 400

        existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
        if existing:
            existing.replaceItems(final_playlist)
        else:
            plex.createPlaylist(playlist_name, items=final_playlist)

        
        run_script_content = f"""from plexapi.server import PlexServer
import random

plex = PlexServer("{data['plex_url']}", "{data['plex_token']}")
selected_keys = {data.get("selectedShows", [])}
playlist_name = "{playlist_name}"

add_commercials = {add_commercials}
commercial_library = "{commercial_library}"
commercial_collection = "{commercial_collection}"
commercial_count = {commercial_count}

add_bumps = {add_bumps}
bump_library = "{bump_library}"
bump_collection = "{bump_collection}"
bump_count = {bump_count}

add_idents = {add_idents}
ident_library = "{ident_library}"
ident_collection = "{ident_collection}"
ident_count = {ident_count}

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

def get_items(section_name, collection_name):
    items = []
    section = plex.library.section(section_name)
    if collection_name:
        collection = next((c for c in section.collections() if c.title == collection_name), None)
        if collection:
            items = collection.items()
    else:
        items = section.all()
    random.shuffle(items)
    return items

commercials = get_items(commercial_library, commercial_collection) if add_commercials else []
bumps = get_items(bump_library, bump_collection) if add_bumps else []
idents = get_items(ident_library, ident_collection) if add_idents else []

final_playlist = []
commercial_index = bump_index = ident_index = 0
total_commercials, total_bumps, total_idents = len(commercials), len(bumps), len(idents)

for ep in ordered_episodes:
    if add_idents and total_idents > 0:
        for _ in range(min(ident_count, total_idents)):
            final_playlist.append(idents[ident_index % total_idents])
            ident_index += 1

    final_playlist.append(ep)

    if add_idents and total_idents > 0:
        for _ in range(min(ident_count, total_idents)):
            final_playlist.append(idents[ident_index % total_idents])
            ident_index += 1

    combined_ads = []
    if add_commercials and total_commercials > 0:
        for _ in range(min(commercial_count, total_commercials)):
            combined_ads.append(commercials[commercial_index % total_commercials])
            commercial_index += 1
    if add_bumps and total_bumps > 0:
        for _ in range(min(bump_count, total_bumps)):
            combined_ads.append(bumps[bump_index % total_bumps])
            bump_index += 1
    random.shuffle(combined_ads)
    final_playlist.extend(combined_ads)

existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
if existing:
    existing.replaceItems(final_playlist)
else:
    plex.createPlaylist(playlist_name, items=final_playlist)

print(f"Playlist '{{playlist_name}}' created with {{len(final_playlist)}} items.")"""

        with open("run_playlist.py", "w") as f:
            f.write(run_script_content)

        cleaner_script_content = f"""from plexapi.server import PlexServer

plex = PlexServer("{data['plex_url']}", "{data['plex_token']}")
playlist_name = "{playlist_name}"

existing = next((p for p in plex.playlists() if p.title == playlist_name), None)
if existing:
    existing.delete()
    print(f"Playlist '{{playlist_name}}' deleted.")
else:
    print(f"Playlist '{{playlist_name}}' not found.")"""

        with open("playlist_cleaner.py", "w") as f:
            f.write(cleaner_script_content)
        return jsonify({"success": True, "count": len(final_playlist)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_seasons_episodes")
def get_seasons_episodes():
    try:
        plex_url = request.args.get("plex_url")
        plex_token = request.args.get("plex_token")
        ratingKey = request.args.get("ratingKey")
        plex = PlexServer(plex_url, plex_token)
        show = plex.fetchItem(int(ratingKey))

        seasons = []
        for season in show.seasons():
            episodes = [{
                "index": ep.index,
                "title": ep.title,
                "ratingKey": ep.ratingKey
            } for ep in season.episodes()]
            seasons.append({
                "seasonNumber": season.index,
                "episodes": episodes
            })

        return jsonify({"success": True, "seasons": seasons})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/load_collections", methods=["POST"])
def load_collections():
    try:
        data = request.get_json()
        plex = PlexServer(data["plex_url"], data["plex_token"])
        section = plex.library.section(data["library"])
        collections = section.collections()
        collection_names = [c.title for c in collections]
        return jsonify({"success": True, "collections": collection_names})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

import webbrowser
import threading

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False)
