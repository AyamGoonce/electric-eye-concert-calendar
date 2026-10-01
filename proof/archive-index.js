(function () {
  "use strict";

  var state = {
    artists: false,
    venues: false,
    genres: false,
    rendered: false
  };

  function normalize(value) {
    return (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function slugify(value) {
    return normalize(value).replace(/\s+/g, "-");
  }

  function sortKey(value) {
    var normalized = normalize(value);

    return normalized.replace(
      /^(?:(?:the|a|an|le|la|les)\s+|l\s+)/,
      ""
    );
  }

  function firstLetter(value) {
    var key = sortKey(value);
    var character = key.charAt(0).toUpperCase();

    return /^[A-Z]$/.test(character) ? character : "#";
  }

  function sortItems(items) {
    return items.sort(function (a, b) {
      return sortKey(a.name).localeCompare(
        sortKey(b.name),
        "en",
        { sensitivity: "base" }
      );
    });
  }

  function makeArtistItems() {
    var lookup =
      window.ElectricEyeArtistLookup &&
      window.ElectricEyeArtistLookup.terms;

    if (!lookup) return null;

    return sortItems(
      Object.keys(lookup).map(function (name) {
        return {
          name: name,
          href:
            "https://archive.electriceyerock.com/artist/" +
            lookup[name] +
            "/",
          meta: ""
        };
      })
    );
  }

  function makeVenueItems() {
    var data = window.ElectricEyeVenueData;

    if (!data) return null;

    return sortItems(
      Object.keys(data).map(function (key) {
        var venue = data[key] || {};
        var name = venue.name || key;
        var meta = venue.city || "";

        if (
          venue.department &&
          venue.department !== "75" &&
          meta
        ) {
          meta += " · " + venue.department;
        }

        return {
          name: name,
          href:
            "https://www.electriceyerock.com/p/venues.html#venue-" +
            slugify(name),
          meta: meta
        };
      })
    );
  }

  function makeGenreItems() {
    var data = window.ElectricEyeGenreData;

    if (!data || !Array.isArray(data.genres)) return null;

    return sortItems(
      data.genres.map(function (genre) {
        return {
          name: genre.name,
          href:
            "https://archive.electriceyerock.com/genre/" +
            slugify(genre.name) +
            "/",
          meta: genre.parent ? "Part of " + genre.parent : ""
        };
      })
    );
  }

  function createAlphabet(items, section) {
    var alphabet = section.querySelector(".ee-index-alphabet");
    var available = Object.create(null);

    items.forEach(function (item) {
      available[firstLetter(item.name)] = true;
    });

    ["#"].concat("ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")).forEach(
      function (letter) {
        var button = document.createElement("button");

        button.type = "button";
        button.className = "ee-index-letter";
        button.textContent = letter;
        button.dataset.letter = letter;

        if (!available[letter]) {
          button.disabled = true;
        }

        alphabet.appendChild(button);
      }
    );
  }

  function createItem(item) {
    var wrapper = document.createElement("div");
    var link = document.createElement("a");

    wrapper.className = "ee-index-item";

    link.href = item.href;
    link.textContent = item.name;
    wrapper.appendChild(link);

    if (item.meta) {
      var meta = document.createElement("span");
      meta.className = "ee-index-meta";
      meta.textContent = item.meta;
      wrapper.appendChild(meta);
    }

    return wrapper;
  }

  function renderItems(section, items, query, activeLetter) {
    var results = section.querySelector(".ee-index-results");
    var normalizedQuery = normalize(query);
    var groups = Object.create(null);

    results.innerHTML = "";

    var filtered = items.filter(function (item) {
      if (
        normalizedQuery &&
        normalize(item.name).indexOf(normalizedQuery) === -1 &&
        normalize(item.meta).indexOf(normalizedQuery) === -1
      ) {
        return false;
      }

      if (
        activeLetter &&
        firstLetter(item.name) !== activeLetter
      ) {
        return false;
      }

      return true;
    });

    if (!filtered.length) {
      var empty = document.createElement("p");
      empty.className = "ee-index-empty";
      empty.textContent = "No matches found.";
      results.appendChild(empty);
      return;
    }

    filtered.forEach(function (item) {
      var letter = firstLetter(item.name);

      if (!groups[letter]) groups[letter] = [];
      groups[letter].push(item);
    });

    ["#"].concat("ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")).forEach(
      function (letter) {
        if (!groups[letter]) return;

        var group = document.createElement("section");
        var heading = document.createElement("h3");
        var itemGrid = document.createElement("div");

        group.className = "ee-index-group";
        group.dataset.letter = letter;

        heading.className = "ee-index-group-letter";
        heading.textContent = letter;

        itemGrid.className = "ee-index-items";

        groups[letter].forEach(function (item) {
          itemGrid.appendChild(createItem(item));
        });

        group.appendChild(heading);
        group.appendChild(itemGrid);
        results.appendChild(group);
      }
    );
  }

  function setupSection(id, items) {
    var section = document.getElementById(id);
    if (!section) return;

    var input = section.querySelector(".ee-index-search");
    var count = section.querySelector(".ee-index-count");
    var activeLetter = "";

    count.textContent =
      items.length.toLocaleString("en") +
      (items.length === 1 ? " entry" : " entries");

    createAlphabet(items, section);
    renderItems(section, items, "", "");

    input.addEventListener("input", function () {
      activeLetter = "";

      section
        .querySelectorAll(".ee-index-letter")
        .forEach(function (button) {
          button.classList.remove("is-active");
        });

      renderItems(section, items, input.value, "");
    });

    section
      .querySelector(".ee-index-alphabet")
      .addEventListener("click", function (event) {
        var button = event.target.closest(".ee-index-letter");

        if (!button || button.disabled) return;

        if (activeLetter === button.dataset.letter) {
          activeLetter = "";
          button.classList.remove("is-active");
        } else {
          activeLetter = button.dataset.letter;

          section
            .querySelectorAll(".ee-index-letter")
            .forEach(function (candidate) {
              candidate.classList.toggle(
                "is-active",
                candidate === button
              );
            });
        }

        renderItems(
          section,
          items,
          input.value,
          activeLetter
        );
      });
  }

  function attemptRender() {
    if (state.rendered) return;

    var artists = makeArtistItems();
    var venues = makeVenueItems();
    var genres = makeGenreItems();

    state.artists = !!artists;
    state.venues = !!venues;
    state.genres = !!genres;

    if (!state.artists || !state.venues || !state.genres) {
      return;
    }

    state.rendered = true;

    setupSection("ee-index-artists", artists);
    setupSection("ee-index-venues", venues);
    setupSection("ee-index-genres", genres);
  }

  document.addEventListener("ee:venue-data-ready", attemptRender);
  document.addEventListener("ee:genre-data-ready", attemptRender);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attemptRender);
  } else {
    attemptRender();
  }
}());
