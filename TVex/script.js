let selectedKeys = new Set();
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
          div.innerHTML = `<img src="${imageUrl}" alt="Poster" loading="lazy" /><div class="title">${show.title}</div>`;
          div.onclick = () => {
            const key = String(div.dataset.key);
            div.classList.toggle("selected");
            selectedKeys.has(key) ? selectedKeys.delete(key) : selectedKeys.add(key);
          };
          container.appendChild(div);
        });

        if (!currentTab) displayLibrary(library);
      } else {
        document.getElementById("status").innerText = "Error: " + data.error;
      }
    });
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
    selectedShows: Array.from(selectedKeys),
    playlistName: document.getElementById("playlistName").value,
    addCommercials: document.getElementById("addCommercials").checked,
    commercialLibrary: document.getElementById("commercialLibrary").value,
    commercialCount: parseInt(document.getElementById("commercialCount").value),
    shuffleEpisodes: document.getElementById("shuffleEpisodes").checked,
    createCollection: document.getElementById("createCollection").checked,
    collectionName: document.getElementById("collectionName").value.trim()
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

function createCollection() {
  const body = {
    plex_url: document.getElementById("plexUrl").value,
    plex_token: document.getElementById("plexToken").value,
    selectedShows: Array.from(selectedKeys),
    library: document.getElementById("library").value.trim(),
    collectionName: document.getElementById("collectionName").value.trim()
  };

  if (!body.collectionName) {
    document.getElementById("status").innerText = "❌ Collection name is required.";
    return;
  }

  fetch("/create_collection", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("status").innerText = data.success
      ? `✅ Collection '${body.collectionName}' created!`
      : `Error: ${data.error}`;
    if (data.success) setTimeout(() => location.reload(), 1500);
  });
}


// Remember Me Feature
window.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("rememberMe") === "true") {
    document.getElementById("plexUrl").value = localStorage.getItem("plexUrl") || "";
    document.getElementById("plexToken").value = localStorage.getItem("plexToken") || "";
    document.getElementById("rememberMe").checked = true;
  }
});

function saveCredentials() {
  const remember = document.getElementById("rememberMe").checked;
  if (remember) {
    localStorage.setItem("plexUrl", document.getElementById("plexUrl").value);
    localStorage.setItem("plexToken", document.getElementById("plexToken").value);
    localStorage.setItem("rememberMe", "true");
  } else {
    localStorage.removeItem("plexUrl");
    localStorage.removeItem("plexToken");
    localStorage.removeItem("rememberMe");
  }
}

document.querySelector("button[onclick='loadShows()']").addEventListener("click", saveCredentials);
document.querySelector("button[onclick='createPlaylist()']").addEventListener("click", saveCredentials);
