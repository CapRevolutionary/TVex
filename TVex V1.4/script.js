let selectedKeys = new Set();
let selectedEpisodes = []; 
let allShowsByLibrary = {};
let loadedLibraries = new Set();
let currentTab = null;

function loadShows() {
  const plexUrl = document.getElementById("plexUrl").value;
  const plexToken = document.getElementById("plexToken").value;
  const libraries = document.getElementById("library").value.split(",").map(s => s.trim());
  const tabContainer = document.getElementById("tabs");
  const container = document.getElementById("showList");

  libraries.forEach(library => {
    if (loadedLibraries.has(library)) return;

    fetch("/load_shows", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plex_url: plexUrl, plex_token: plexToken, library })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        allShowsByLibrary[library] = data.shows;
        loadedLibraries.add(library);

        const tabBtn = document.createElement("button");
        tabBtn.textContent = library;
        tabBtn.classList.add("tab-button");
        tabBtn.onclick = () => displayLibrary(library);
        tabContainer.appendChild(tabBtn);

        data.shows.forEach(show => {
          const div = document.createElement("div");
          div.classList.add("show-card");
          div.dataset.key = show.ratingKey;
          div.dataset.library = library;
          div.style.display = "none";

          const imageUrl = `${plexUrl}${show.thumb}?X-Plex-Token=${plexToken}&width=120&height=180&quality=60`;
          div.innerHTML = `
            <img src="${imageUrl}" alt="Poster" loading="lazy" />
            <div class="title">${show.title}</div>
            <div style="margin-top: 10px;">
              <select class="season-select" data-key="${show.ratingKey}"><option value="">Season</option></select>
              <button class="add-episode" data-key="${show.ratingKey}">Add</button>
              <select class="episode-select" data-key="${show.ratingKey}"><option value="">Episode</option></select>
            </div>
          `;

          div.querySelector(".add-episode").onclick = (e) => {
            e.stopPropagation();
            const seasonSelect = div.querySelector(".season-select");
            const episodeSelect = div.querySelector(".episode-select");
            const seasonNumber = seasonSelect.value;
            const episodeNumber = episodeSelect.value;
            if (seasonNumber && episodeNumber) {
              selectedEpisodes.push({
                ratingKey: div.dataset.key,
                season: parseInt(seasonNumber),
                episode: parseInt(episodeNumber)
              });
              div.classList.add("selected");
            }
          };

          div.querySelector("img").onclick = (e) => {
            e.stopPropagation();
            const key = String(div.dataset.key);
            div.classList.toggle("selected");
            selectedKeys.has(key) ? selectedKeys.delete(key) : selectedKeys.add(key);
          };

          container.appendChild(div);

          fetch(`/get_seasons_episodes?plex_url=${encodeURIComponent(plexUrl)}&plex_token=${encodeURIComponent(plexToken)}&ratingKey=${show.ratingKey}`)
            .then(res => res.json())
            .then(seData => {
              if (seData.success) {
                const seasons = seData.seasons;
                const seasonSelect = div.querySelector(".season-select");
                seasons.forEach(season => {
                  const opt = document.createElement("option");
                  opt.value = season.seasonNumber;
                  opt.textContent = `Season ${season.seasonNumber}`;
                  seasonSelect.appendChild(opt);
                });

                seasonSelect.onchange = () => {
                  const selectedSeason = parseInt(seasonSelect.value);
                  const episodeSelect = div.querySelector(".episode-select");
                  episodeSelect.innerHTML = '<option value="">Episode</option>';
                  const selectedSeasonData = seasons.find(s => s.seasonNumber === selectedSeason);
                  if (selectedSeasonData) {
                    selectedSeasonData.episodes.forEach(episode => {
                      const epOpt = document.createElement("option");
                      epOpt.value = episode.index;
                      epOpt.textContent = `Ep ${episode.index}: ${episode.title}`;
                      episodeSelect.appendChild(epOpt);
                    });
                  }
                };
              }
            })
            .catch(error => {
              console.error("Failed to load seasons/episodes", error);
            });
        });

        if (!currentTab) displayLibrary(library);
      } else {
        document.getElementById("status").innerText = "Error: " + data.error;
      }
    });
  });

  // 🛠️ Always load collections independently after shows
  loadCollections("commercialLibrary", "commercialCollection");
  loadCollections("bumpLibrary", "bumpCollection");
  loadCollections("identLibrary", "identCollection");

  document.getElementById("bumpLibrary").addEventListener("change", () => {
    loadCollections("bumpLibrary", "bumpCollection");
  });

  document.getElementById("identLibrary").addEventListener("change", () => {
    loadCollections("identLibrary", "identCollection");
  });
}

function displayLibrary(library) {
  currentTab = library;
  document.querySelectorAll("#tabs button").forEach(btn => {
    btn.classList.toggle("active-tab", btn.textContent === library);
  });
  document.querySelectorAll(".show-card").forEach(card => {
    card.style.display = card.dataset.library === library ? "block" : "none";
  });
}

function createPlaylist() {
  const body = {
    plex_url: document.getElementById("plexUrl").value,
    plex_token: document.getElementById("plexToken").value,
    playlistName: document.getElementById("playlistName").value,
    addCommercials: document.getElementById("addCommercials").checked,
    commercialLibrary: document.getElementById("commercialLibrary").value,
    commercialCollection: document.getElementById("commercialCollection").value,
    commercialCount: parseInt(document.getElementById("commercialCount").value),
    addBumps: document.getElementById("addBumps").checked,
    bumpLibrary: document.getElementById("bumpLibrary").value,
    bumpCollection: document.getElementById("bumpCollection").value,
    bumpCount: parseInt(document.getElementById("bumpCount").value),
    addIdents: document.getElementById("addIdents").checked,
    identLibrary: document.getElementById("identLibrary").value,
    identCollection: document.getElementById("identCollection").value,
    identCount: parseInt(document.getElementById("identCount").value),
    shuffleEpisodes: document.getElementById("shuffleEpisodes").checked,
    createCollection: document.getElementById("createCollection").checked,
    collectionName: document.getElementById("collectionName").value.trim(),
    selectedShows: Array.from(selectedKeys),
    selectedEpisodes: selectedEpisodes
  };

  fetch("/create_playlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("status").innerText = data.success
      ? `✅ Playlist created with ${data.count} episodes!`
      : `Error: ${data.error}`;
    if (data.success) setTimeout(() => location.reload(), 1500);
  });
}

function loadCollections(libraryInputId, collectionSelectId) {
  const plexUrl = document.getElementById("plexUrl").value;
  const plexToken = document.getElementById("plexToken").value;
  const libraryName = document.getElementById(libraryInputId).value;
  const collectionSelect = document.getElementById(collectionSelectId);

  if (!libraryName) return;

  fetch("/load_collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plex_url: plexUrl, plex_token: plexToken, library: libraryName })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      collectionSelect.innerHTML = '<option value="">Select Collection (optional)</option>';
      data.collections.forEach(name => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        collectionSelect.appendChild(opt);
      });
    }
  });
}
