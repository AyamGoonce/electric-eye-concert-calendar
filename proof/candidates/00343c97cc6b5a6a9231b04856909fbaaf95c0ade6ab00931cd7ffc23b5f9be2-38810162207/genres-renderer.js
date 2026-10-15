(function () {
  "use strict";

  var MOUNT_ID = "ee-genres";
  var READY = "ee:genre-data-ready";
  var ERROR = "ee:genre-data-error";
  var initialized = false;
  var records = [];
  var controls = null;

  function normalize(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase();
  }

  function slug(value) {
    return normalize(value)
      .replace(/['’]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function cmp(a, b) {
    return String(a).localeCompare(String(b), "en", {
      sensitivity: "base"
    });
  }

  function el(tag, cls, value) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (value !== undefined && value !== null) {
      node.textContent = value;
    }
    return node;
  }

  function stat(parent, value, label) {
    var box = el("div", "ee-g-stat");
    box.append(
      el("strong", "", Number(value).toLocaleString("en-GB")),
      el("span", "", label)
    );
    parent.append(box);
  }

  function publicRecords(data) {
    return (data.genres || [])
      .map(function (source) {
        return {
          name: source.name || "",
          slug: slug(source.name || ""),
          parent: source.parent || "",
          artistCount: Number(source.artistCount || 0),
          directArtistCount: Number(source.directArtistCount || 0),
          artists: Array.isArray(source.artists) ? source.artists : [],
          directArtists: Array.isArray(source.directArtists)
            ? source.directArtists
            : []
        };
      })
      .filter(function (record) {
        return record.name && record.artistCount;
      });
  }

  function buildShell(mount, data) {
    mount.replaceChildren();

    var hero = el("header", "ee-g-hero");
    var heroShell = el("div", "ee-g-shell");

    heroShell.append(
      el("div", "ee-g-kicker", "Electric Eye genre archive"),
      el("h1", "ee-g-title", "Genres"),
      el(
        "p",
        "ee-g-intro",
        "Explore the artists and styles covered by Electric Eye, from broad genres to more specific subgenres."
      )
    );

    var stats = el("div", "ee-g-stats");

    stat(stats, records.length, "Genres");
    stat(
      stats,
      data.resolvedArtistCount || 0,
      "Indexed artists"
    );
    stat(
      stats,
      records.filter(function (record) {
        return !record.parent;
      }).length,
      "Main genres"
    );

    heroShell.append(stats);
    hero.append(heroShell);
    mount.append(hero);

    var directory = el("section", "ee-g-section");
    var shell = el("div", "ee-g-shell");

    var head = el("div", "ee-g-section-head");
    head.append(
      el("h2", "", "Genre directory"),
      el(
        "p",
        "",
        "Search by genre, subgenre or artist. Open a genre to see the artists currently associated with it."
      )
    );

    shell.append(head);

    var tools = el("div", "ee-g-tools");

    var search = el("input", "ee-g-search");
    search.type = "search";
    search.placeholder = "Search genre or artist…";
    search.autocomplete = "off";
    search.setAttribute("aria-label", "Search genres");

    var filter = el("select", "ee-g-filter");
    filter.setAttribute("aria-label", "Filter genres");

    [
      ["all", "All genres"],
      ["roots", "Main genres only"],
      ["subgenres", "Subgenres only"]
    ].forEach(function (item) {
      var option = el("option", "", item[1]);
      option.value = item[0];
      filter.append(option);
    });

    var sort = el("select", "ee-g-sort");
    sort.setAttribute("aria-label", "Sort genres");

    [
      ["name", "Genre A–Z"],
      ["artists", "Most artists"]
    ].forEach(function (item) {
      var option = el("option", "", item[1]);
      option.value = item[0];
      sort.append(option);
    });

    var reset = el("button", "ee-g-reset", "Reset");
    reset.type = "button";

    tools.append(search, filter, sort, reset);
    shell.append(tools);

    var resultCount = el("div", "ee-g-results");
    resultCount.setAttribute("aria-live", "polite");
    shell.append(resultCount);

    var grid = el("div", "ee-g-grid");
    shell.append(grid);

    var noResults = el(
      "div",
      "ee-g-no-results",
      "No genres match this search."
    );
    noResults.hidden = true;
    shell.append(noResults);

    directory.append(shell);
    mount.append(directory);

    return {
      search: search,
      filter: filter,
      sort: sort,
      reset: reset,
      resultCount: resultCount,
      grid: grid,
      noResults: noResults
    };
  }

  function setCardOpen(article, open) {
    var summary = article.querySelector(".ee-g-card-summary");
    var details = article.querySelector(".ee-g-card-details");
    var symbol = article.querySelector(".ee-g-card-chevron");

    if (!summary || !details) return;

    article.classList.toggle("ee-g-card-open", open);
    summary.setAttribute("aria-expanded", String(open));
    details.hidden = !open;

    if (symbol) {
      symbol.textContent = open ? "−" : "+";
    }
  }

  function artistList(parent, record) {
    var list = el("div", "ee-g-artists");
    var limit = 16;
    var expanded = false;

    function draw() {
      list.replaceChildren();

      record.artists
        .slice(0, expanded ? record.artists.length : limit)
        .forEach(function (artist) {
          list.append(el("span", "ee-g-artist", artist));
        });

      toggle.textContent = expanded
        ? "Show fewer"
        : "Show all " + record.artists.length + " artists";

      toggle.hidden = record.artists.length <= limit;
    }

    var toggle = el("button", "ee-g-more");
    toggle.type = "button";
    toggle.addEventListener("click", function () {
      expanded = !expanded;
      draw();
    });

    parent.append(list, toggle);
    draw();
  }

  function card(record) {
    var article = el("article", "ee-g-card");
    article.id = "genre-" + record.slug;

    var summary = el("button", "ee-g-card-summary");
    summary.type = "button";
    summary.setAttribute("aria-expanded", "false");

    var main = el("div", "ee-g-card-summary-main");
    main.append(el("h3", "", record.name));

    if (record.parent) {
      main.append(
        el("p", "ee-g-parent", record.parent)
      );
    } else {
      main.append(
        el("p", "ee-g-parent", "Main genre")
      );
    }

    var side = el("div", "ee-g-card-summary-side");

    side.append(
      el(
        "span",
        "ee-g-count",
        record.artistCount +
          (record.artistCount === 1 ? " artist" : " artists")
      ),
      el("span", "ee-g-card-chevron", "+")
    );

    summary.append(main, side);

    var details = el("div", "ee-g-card-details");
    details.id = "genre-details-" + record.slug;
    details.hidden = true;

    summary.setAttribute("aria-controls", details.id);
    summary.setAttribute(
      "aria-label",
      "Open " + record.name + " genre"
    );

    summary.addEventListener("click", function () {
      setCardOpen(
        article,
        !article.classList.contains("ee-g-card-open")
      );
    });

    var info = el("div", "ee-g-detail-meta");

    if (record.parent) {
      info.append(
        el("span", "", "Parent: " + record.parent)
      );
    }

    if (
      record.directArtistCount &&
      record.directArtistCount !== record.artistCount
    ) {
      info.append(
        el(
          "span",
          "",
          record.directArtistCount +
            " directly classified · " +
            record.artistCount +
            " including subgenres"
        )
      );
    }

    details.append(info);

    var artistsBlock = el("div", "ee-g-block");
    artistsBlock.append(el("h4", "", "Artists"));
    artistList(artistsBlock, record);
    details.append(artistsBlock);

    article.append(summary, details);

    return article;
  }

  function filteredRecords() {
    var query = normalize(controls.search.value.trim());
    var mode = controls.filter.value;

    var filtered = records.filter(function (record) {
      if (mode === "roots" && record.parent) return false;
      if (mode === "subgenres" && !record.parent) return false;

      if (!query) return true;

      return normalize(
        [
          record.name,
          record.parent,
          record.artists.join(" ")
        ].join(" ")
      ).includes(query);
    });

    if (controls.sort.value === "artists") {
      filtered.sort(function (a, b) {
        return b.artistCount - a.artistCount || cmp(a.name, b.name);
      });
    } else {
      filtered.sort(function (a, b) {
        return cmp(a.name, b.name);
      });
    }

    return filtered;
  }

  function render() {
    var visible = filteredRecords();
    var fragment = document.createDocumentFragment();

    visible.forEach(function (record) {
      fragment.append(card(record));
    });

    controls.grid.replaceChildren(fragment);
    controls.grid.hidden = !visible.length;
    controls.noResults.hidden = !!visible.length;

    controls.resultCount.innerHTML =
      "<strong>" +
      visible.length.toLocaleString("en-GB") +
      "</strong> " +
      (visible.length === 1 ? "genre" : "genres");

    highlightHash(false);
  }

  function highlightHash(scroll) {
    if (!/^#genre-/.test(location.hash)) return;

    var target = document.getElementById(location.hash.slice(1));
    if (!target) return;

    document
      .querySelectorAll(".ee-g-highlight")
      .forEach(function (node) {
        node.classList.remove("ee-g-highlight");
      });

    target.classList.add("ee-g-highlight");
    setCardOpen(target, true);

    if (scroll !== false) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  }

  function showFailure(reason) {
    var mount = document.getElementById(MOUNT_ID);
    if (!mount || initialized) return;

    mount.replaceChildren(
      el(
        "p",
        "ee-g-error",
        reason || "Genre data could not be loaded."
      )
    );
  }

  function initialize() {
    var mount = document.getElementById(MOUNT_ID);
    var data = window.ElectricEyeGenreData;

    if (!mount || !data || initialized) return;

    initialized = true;
    records = publicRecords(data);
    controls = buildShell(mount, data);

    controls.search.addEventListener("input", render);
    controls.filter.addEventListener("change", render);
    controls.sort.addEventListener("change", render);

    controls.reset.addEventListener("click", function () {
      controls.search.value = "";
      controls.filter.value = "all";
      controls.sort.value = "name";
      render();
    });

    window.addEventListener("hashchange", function () {
      highlightHash(true);
    });

    render();
  }

  document.addEventListener("DOMContentLoaded", initialize);
  document.addEventListener(READY, initialize);
  document.addEventListener(ERROR, function () {
    showFailure("Genre data could not be loaded.");
  });

  initialize();
}());
