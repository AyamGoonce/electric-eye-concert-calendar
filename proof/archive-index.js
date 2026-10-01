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

  function hasEditorialCoverage(content, slug) {
    var artist =
      content &&
      content.artists &&
      content.artists[slug];

    return !!(
      artist &&
      Array.isArray(artist.ar) &&
      artist.ar.length
    );
  }

  function makeArtistItems() {
    var lookup =
      window.ElectricEyeArtistLookup &&
      window.ElectricEyeArtistLookup.terms;
    var content = window.ElectricEyeContentIndex;

    if (!lookup || !content || !content.artists) return null;

    return sortItems(
      Object.keys(lookup)
        .filter(function (name) {
          return hasEditorialCoverage(content, lookup[name]);
        })
        .map(function (name) {
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
      Object.keys(data)
        .filter(function (key) {
          var venue = data[key] || {};

          return (
            (Array.isArray(venue.articles) &&
              venue.articles.length > 0) ||
            (Array.isArray(venue.events) &&
              venue.events.length > 0)
          );
        })
        .map(function (key) {
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
    var lookup =
      window.ElectricEyeArtistLookup &&
      window.ElectricEyeArtistLookup.terms;
    var content = window.ElectricEyeContentIndex;
    var concerts = window.ElectricEyeConcertData;

    if (
      !data ||
      !Array.isArray(data.genres) ||
      !lookup ||
      !content ||
      !content.artists ||
      !Array.isArray(concerts)
    ) {
      return null;
    }

    var calendarArtists = Object.create(null);

    concerts.forEach(function (event) {
      [event.h]
        .concat(event.ch || [], event.o || [])
        .filter(Boolean)
        .forEach(function (name) {
          calendarArtists[normalize(name)] = true;
        });
    });

    var items = data.genres.map(function (genre) {
      var visibleArtists = (genre.artists || []).filter(
        function (name) {
          var slug = lookup[name];
          var articleBacked =
            slug && hasEditorialCoverage(content, slug);
          var calendarBacked =
            !!calendarArtists[normalize(name)];

          return articleBacked || calendarBacked;
        }
      );

      return {
        name: genre.name,
        parent: genre.parent || "",
        href:
          "https://archive.electriceyerock.com/genre/" +
          slugify(genre.name) +
          "/",
        artistCount: visibleArtists.length
      };
    });

    var byName = Object.create(null);
    var children = Object.create(null);

    items.forEach(function (item) {
      byName[item.name] = item;
      children[item.name] = [];
    });

    items.forEach(function (item) {
      if (item.parent && byName[item.parent]) {
        children[item.parent].push(item);
      }
    });

    var keepMemo = Object.create(null);

    function shouldKeep(item) {
      if (Object.prototype.hasOwnProperty.call(keepMemo, item.name)) {
        return keepMemo[item.name];
      }

      var keep =
        item.artistCount > 0 ||
        children[item.name].some(shouldKeep);

      keepMemo[item.name] = keep;
      return keep;
    }

    return sortItems(items.filter(shouldKeep));
  }

  function setupCollapsible(section) {
    var heading = section.querySelector(".ee-index-heading");
    var body = section.querySelector(".ee-index-body");

    if (!heading || !body) return;

    function setOpen(open) {
      heading.setAttribute("aria-expanded", open ? "true" : "false");
      body.hidden = !open;
      section.classList.toggle("is-open", open);
    }

    heading.addEventListener("click", function () {
      setOpen(heading.getAttribute("aria-expanded") !== "true");
    });

    setOpen(false);
  }

  function createAlphabet(items, section) {
    var alphabet = section.querySelector(".ee-index-alphabet");
    var available = Object.create(null);

    if (!alphabet) return;

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
    setupCollapsible(section);

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

  function buildGenreTree(items) {
    var byName = Object.create(null);
    var children = Object.create(null);
    var roots = [];

    items.forEach(function (item) {
      byName[item.name] = item;
      children[item.name] = [];
    });

    items.forEach(function (item) {
      if (item.parent && byName[item.parent]) {
        children[item.parent].push(item);
      } else {
        roots.push(item);
      }
    });

    Object.keys(children).forEach(function (name) {
      sortItems(children[name]);
    });

    sortItems(roots);

    return {
      roots: roots,
      children: children
    };
  }

  function genreMatches(item, tree, query) {
    if (!query) return true;

    if (normalize(item.name).indexOf(query) !== -1) {
      return true;
    }

    return tree.children[item.name].some(function (child) {
      return genreMatches(child, tree, query);
    });
  }

  function createGenreNode(item, tree, query, ancestorMatched) {
    var children = tree.children[item.name] || [];
    var selfMatches =
      !query ||
      normalize(item.name).indexOf(query) !== -1;
    var showAllDescendants = ancestorMatched || selfMatches;
    var visibleChildren = children.filter(function (child) {
      return (
        showAllDescendants ||
        genreMatches(child, tree, query)
      );
    });

    var node = document.createElement("div");
    var row = document.createElement("div");
    var link = document.createElement("a");
    var meta = document.createElement("span");

    node.className = "ee-genre-node";
    row.className = "ee-genre-row";

    link.className = "ee-genre-link";
    link.href = item.href;
    link.textContent = item.name;

    meta.className = "ee-genre-count";
    meta.textContent =
      item.artistCount.toLocaleString("en") +
      (item.artistCount === 1 ? " artist" : " artists");

    if (visibleChildren.length) {
      var toggle = document.createElement("button");
      var childContainer = document.createElement("div");
      var openForSearch = !!query;

      toggle.type = "button";
      toggle.className = "ee-genre-toggle";
      toggle.setAttribute(
        "aria-label",
        "Toggle " + item.name + " subgenres"
      );
      toggle.setAttribute(
        "aria-expanded",
        openForSearch ? "true" : "false"
      );
      toggle.textContent = "›";

      childContainer.className = "ee-genre-children";
      childContainer.hidden = !openForSearch;

      visibleChildren.forEach(function (child) {
        childContainer.appendChild(
          createGenreNode(
            child,
            tree,
            query,
            showAllDescendants
          )
        );
      });

      toggle.addEventListener("click", function () {
        var open =
          toggle.getAttribute("aria-expanded") !== "true";

        toggle.setAttribute(
          "aria-expanded",
          open ? "true" : "false"
        );
        childContainer.hidden = !open;
      });

      row.appendChild(toggle);
      node.appendChild(row);
      node.appendChild(childContainer);
    } else {
      var spacer = document.createElement("span");
      spacer.className = "ee-genre-toggle-spacer";
      row.appendChild(spacer);
      node.appendChild(row);
    }

    row.appendChild(link);
    row.appendChild(meta);

    return node;
  }

  function renderGenreTree(section, items, tree, query) {
    var results = section.querySelector(".ee-index-results");
    var normalizedQuery = normalize(query);

    results.innerHTML = "";

    var visibleRoots = tree.roots.filter(function (root) {
      return genreMatches(root, tree, normalizedQuery);
    });

    if (!visibleRoots.length) {
      var empty = document.createElement("p");

      empty.className = "ee-index-empty";
      empty.textContent = "No matches found.";
      results.appendChild(empty);
      return;
    }

    visibleRoots.forEach(function (root) {
      results.appendChild(
        createGenreNode(root, tree, normalizedQuery, false)
      );
    });
  }

  function setupGenreSection(id, items) {
    var section = document.getElementById(id);

    if (!section) return;

    var input = section.querySelector(".ee-index-search");
    var count = section.querySelector(".ee-index-count");
    var tree = buildGenreTree(items);

    count.textContent =
      items.length.toLocaleString("en") +
      (items.length === 1 ? " genre" : " genres");

    renderGenreTree(section, items, tree, "");
    setupCollapsible(section);

    input.addEventListener("input", function () {
      renderGenreTree(section, items, tree, input.value);
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
    setupGenreSection("ee-index-genres", genres);
  }

  document.addEventListener("ee:content-index-ready", attemptRender);
  document.addEventListener("ee:concert-data-ready", attemptRender);
  document.addEventListener("ee:venue-data-ready", attemptRender);
  document.addEventListener("ee:genre-data-ready", attemptRender);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attemptRender);
  } else {
    attemptRender();
  }
}());
