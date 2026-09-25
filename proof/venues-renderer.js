(function () {
  "use strict";

  var MOUNT_ID = "ee-venues";
  var READY = "ee:venue-data-ready";
  var ERROR = "ee:venue-data-error";
  var initialized = false;
  var map = null;
  var markerLayer = null;
  var markers = new Map();
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
    return String(a).localeCompare(String(b), "fr", {
      sensitivity: "base"
    });
  }

  function el(tag, cls, value) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (value !== undefined && value !== null) node.textContent = value;
    return node;
  }

  function articleDate(value) {
    if (!value) return "";
    var parts = value.split("-").map(Number);
    if (parts.length !== 3) return value;
    return new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      timeZone: "UTC"
    }).format(new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])));
  }

  function eventDate(value) {
    return articleDate(value);
  }

  function venueHref(record) {
    return "#venue-" + record.slug;
  }

  function calendarHref(event) {
    return "/p/calendar.html#event-" + encodeURIComponent(event.eventId);
  }

  function publicRecords(raw) {
    return Object.keys(raw)
      .map(function (name) {
        var source = raw[name] || {};
        return {
          name: source.name || name,
          slug: slug(source.name || name),
          city: source.city || "",
          department: source.department || "",
          address: source.address || "",
          lat: source.lat,
          lng: source.lng,
          website: source.website || "",
          mapReady: source.mapReady === true,
          events: Array.isArray(source.events) ? source.events : [],
          articles: Array.isArray(source.articles) ? source.articles : []
        };
      })
      .filter(function (record) {
        return record.events.length || record.articles.length;
      });
  }

  function stat(parent, value, label) {
    var box = el("div", "ee-v-stat");
    box.append(
      el("strong", "", Number(value).toLocaleString("en-GB")),
      el("span", "", label)
    );
    parent.append(box);
  }

  function buildShell(mount) {
    mount.replaceChildren();

    var hero = el("header", "ee-v-hero");
    var heroShell = el("div", "ee-v-shell");

    heroShell.append(
      el("div", "ee-v-kicker", "Electric Eye venue archive"),
      el("h1", "ee-v-title", "Venues"),
      el(
        "p",
        "ee-v-intro",
        "Explore concert venues covered by Electric Eye, find upcoming shows and browse the live archive."
      )
    );

    var stats = el("div", "ee-v-stats");
    stat(stats, records.length, "Venues");
    stat(
      stats,
      records.filter(function (r) { return r.mapReady; }).length,
      "Mapped"
    );
    stat(
      stats,
      records.reduce(function (n, r) { return n + r.events.length; }, 0),
      "Upcoming concerts"
    );
    stat(
      stats,
      records.reduce(function (n, r) { return n + r.articles.length; }, 0),
      "Archive articles"
    );

    heroShell.append(stats);
    hero.append(heroShell);
    mount.append(hero);

    var mapSection = el("section", "ee-v-section");
    var mapShell = el("div", "ee-v-shell");
    var mapHead = el("div", "ee-v-section-head");
    mapHead.append(
      el("h2", "", "Venue map"),
      el(
        "p",
        "",
        "Select a marker to open its venue entry. Historical and unmapped locations remain available in the directory below."
      )
    );
    mapShell.append(mapHead);

    var mapNode = el("div", "ee-v-map");
    mapNode.id = "ee-v-map";
    mapNode.setAttribute("aria-label", "Map of Electric Eye venues");
    mapShell.append(mapNode);
    mapSection.append(mapShell);
    mount.append(mapSection);

    var directory = el("section", "ee-v-section");
    var directoryShell = el("div", "ee-v-shell");
    var dirHead = el("div", "ee-v-section-head");

    dirHead.append(
      el("h2", "", "Venue directory"),
      el(
        "p",
        "",
        "Search venues, cities or addresses, then open upcoming concerts or Electric Eye coverage."
      )
    );

    directoryShell.append(dirHead);

    var tools = el("div", "ee-v-tools");

    var search = el("input", "ee-v-search");
    search.type = "search";
    search.placeholder = "Search venue, city or address…";
    search.autocomplete = "off";
    search.setAttribute("aria-label", "Search venues");

    var sort = el("select", "ee-v-sort");
    sort.setAttribute("aria-label", "Sort venues");

    [
      ["name", "Venue A–Z"],
      ["events", "Most upcoming concerts"],
      ["articles", "Most Electric Eye articles"]
    ].forEach(function (item) {
      var option = el("option", "", item[1]);
      option.value = item[0];
      sort.append(option);
    });

    var reset = el("button", "ee-v-reset", "Reset");
    reset.type = "button";

    tools.append(search, sort, reset);
    directoryShell.append(tools);

    var resultCount = el("div", "ee-v-results");
    resultCount.setAttribute("aria-live", "polite");
    directoryShell.append(resultCount);

    var grid = el("div", "ee-v-grid");
    directoryShell.append(grid);

    var noResults = el(
      "div",
      "ee-v-no-results",
      "No venues match this search."
    );
    noResults.hidden = true;
    directoryShell.append(noResults);

    directory.append(directoryShell);
    mount.append(directory);

    return {
      mapNode: mapNode,
      search: search,
      sort: sort,
      reset: reset,
      resultCount: resultCount,
      grid: grid,
      noResults: noResults
    };
  }

  function popupFor(record) {
    var box = el("div", "ee-v-popup");
    box.append(el("strong", "", record.name));

    var location = [record.address, record.city]
      .filter(Boolean)
      .join(" · ");

    if (location) {
      box.append(el("div", "ee-v-popup-meta", location));
    }

    var summary = [];
    if (record.events.length) {
      summary.push(
        record.events.length +
        (record.events.length === 1 ? " upcoming concert" : " upcoming concerts")
      );
    }
    if (record.articles.length) {
      summary.push(
        record.articles.length +
        (record.articles.length === 1 ? " Electric Eye article" : " Electric Eye articles")
      );
    }

    if (summary.length) {
      box.append(el("div", "ee-v-popup-meta", summary.join(" · ")));
    }

    var link = el("a", "", "Open venue");
    link.href = venueHref(record);
    link.addEventListener("click", function () {
      setTimeout(highlightHashVenue, 0);
    });
    box.append(link);

    return box;
  }

  function initializeMap() {
    if (!window.L || !controls.mapNode) return;

    map = L.map(controls.mapNode, {
      scrollWheelZoom: false
    });

    L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
      }
    ).addTo(map);

    markerLayer = L.layerGroup().addTo(map);

    map.on("focus", function () {
      map.scrollWheelZoom.enable();
    });

    map.on("blur", function () {
      map.scrollWheelZoom.disable();
    });

    renderMarkers(records);
  }

  function renderMarkers(visible) {
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();
    markers.clear();

    var bounds = [];

    visible.forEach(function (record) {
      if (
        !record.mapReady ||
        typeof record.lat !== "number" ||
        typeof record.lng !== "number"
      ) return;

      var marker = L.marker([record.lat, record.lng]);
      marker.bindPopup(popupFor(record));
      marker.addTo(markerLayer);

      markers.set(record.slug, marker);
      bounds.push([record.lat, record.lng]);
    });

    if (bounds.length) {
      map.fitBounds(bounds, {
        padding: [30, 30],
        maxZoom: 12
      });
    } else {
      map.setView([48.8566, 2.3522], 10);
    }
  }

  function itemMeta(parent, value) {
    if (value) parent.append(el("span", "ee-v-item-meta", value));
  }

  function eventList(parent, record) {
    var block = el("div", "ee-v-block");
    block.append(el("h4", "", "Upcoming concerts"));

    if (!record.events.length) {
      block.append(
        el("div", "ee-v-empty-block", "No upcoming concerts currently indexed.")
      );
      parent.append(block);
      return;
    }

    var list = el("ul", "ee-v-list");
    var limit = 4;
    var expanded = false;

    function draw() {
      list.replaceChildren();

      record.events
        .slice(0, expanded ? record.events.length : limit)
        .forEach(function (event) {
          var li = el("li");
          var link = el("a", "ee-v-event-title", event.headliner);
          link.href = calendarHref(event);

          var detail = eventDate(event.date);
          if (event.startTime) detail += " · " + event.startTime;
          if (event.soldOut) detail += " · SOLD OUT";

          li.append(link);
          itemMeta(li, detail);
          list.append(li);
        });

      toggle.textContent = expanded
        ? "Show fewer"
        : "Show all " + record.events.length + " concerts";

      toggle.hidden = record.events.length <= limit;
    }

    var toggle = el("button", "ee-v-more");
    toggle.type = "button";
    toggle.addEventListener("click", function () {
      expanded = !expanded;
      draw();
    });

    block.append(list, toggle);
    draw();
    parent.append(block);
  }

  function articleList(parent, record) {
    var block = el("div", "ee-v-block");
    block.append(el("h4", "", "From the Electric Eye archive"));

    if (!record.articles.length) {
      block.append(
        el("div", "ee-v-empty-block", "No Electric Eye articles currently indexed.")
      );
      parent.append(block);
      return;
    }

    var list = el("ul", "ee-v-list");
    var limit = 4;
    var expanded = false;

    function draw() {
      list.replaceChildren();

      record.articles
        .slice(0, expanded ? record.articles.length : limit)
        .forEach(function (article) {
          var li = el("li");
          var link = el("a", "ee-v-article-title", article.title);
          link.href = article.url;
          li.append(link);
          itemMeta(li, articleDate(article.date));
          list.append(li);
        });

      toggle.textContent = expanded
        ? "Show fewer"
        : "Show all " + record.articles.length + " articles";

      toggle.hidden = record.articles.length <= limit;
    }

    var toggle = el("button", "ee-v-more");
    toggle.type = "button";
    toggle.addEventListener("click", function () {
      expanded = !expanded;
      draw();
    });

    block.append(list, toggle);
    draw();
    parent.append(block);
  }

  function card(record) {
    var article = el("article", "ee-v-card");
    article.id = "venue-" + record.slug;

    var head = el("div", "ee-v-card-head");
    var titleRow = el("div", "ee-v-card-title-row");
    titleRow.append(el("h3", "", record.name));
    head.append(titleRow);

    var locationParts = [];
    if (record.address) locationParts.push(record.address);
    else if (record.city) locationParts.push(record.city);

    if (record.address && record.city &&
        normalize(record.address).indexOf(normalize(record.city)) === -1) {
      locationParts.push(record.city);
    }

    if (locationParts.length) {
      head.append(el("p", "ee-v-location", locationParts.join(" · ")));
    }

    var actions = el("div", "ee-v-card-actions");

    if (record.website) {
      var website = el("a", "", "Official website ↗");
      website.href = record.website;
      website.target = "_blank";
      website.rel = "noopener noreferrer";
      actions.append(website);
    }

    if (record.mapReady) {
      var mapButton = el("button", "ee-v-map-button", "Show on map");
      mapButton.type = "button";
      mapButton.addEventListener("click", function () {
        var marker = markers.get(record.slug);
        if (!map || !marker) return;

        map.flyTo([record.lat, record.lng], 15, {
          duration: 0.6
        });
        marker.openPopup();
        controls.mapNode.scrollIntoView({
          behavior: "smooth",
          block: "center"
        });
      });
      actions.append(mapButton);
    }

    var permalink = el("a", "", "Permalink");
    permalink.href = venueHref(record);
    actions.append(permalink);

    head.append(actions);

    var counts = el("div", "ee-v-counts");
    counts.append(
      el(
        "span",
        "",
        record.events.length + (record.events.length === 1 ? " upcoming" : " upcoming")
      ),
      el(
        "span",
        "",
        record.articles.length + (record.articles.length === 1 ? " article" : " articles")
      )
    );
    head.append(counts);

    var body = el("div", "ee-v-card-body");
    eventList(body, record);
    articleList(body, record);

    article.append(head, body);
    return article;
  }

  function filteredRecords() {
    var query = normalize(controls.search.value.trim());

    var filtered = records.filter(function (record) {
      if (!query) return true;

      return normalize([
        record.name,
        record.city,
        record.department,
        record.address
      ].join(" ")).includes(query);
    });

    var sort = controls.sort.value;

    filtered.sort(
      sort === "events"
        ? function (a, b) {
            return b.events.length - a.events.length || cmp(a.name, b.name);
          }
        : sort === "articles"
        ? function (a, b) {
            return b.articles.length - a.articles.length || cmp(a.name, b.name);
          }
        : function (a, b) {
            return cmp(a.name, b.name);
          }
    );

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
      (visible.length === 1 ? "venue" : "venues");

    renderMarkers(visible);
    highlightHashVenue(false);
  }

  function highlightHashVenue(scroll) {
    if (!/^#venue-/.test(location.hash)) return;

    var target = document.getElementById(location.hash.slice(1));
    if (!target) return;

    document.querySelectorAll(".ee-v-highlight").forEach(function (node) {
      node.classList.remove("ee-v-highlight");
    });

    target.classList.add("ee-v-highlight");

    if (scroll !== false) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }

    var slugValue = location.hash.replace(/^#venue-/, "");
    var marker = markers.get(slugValue);

    if (marker && map) {
      marker.openPopup();
    }
  }

  function showFailure(reason) {
    var mount = document.getElementById(MOUNT_ID);
    if (!mount || initialized) return;

    mount.replaceChildren(
      el(
        "div",
        "ee-v-failure",
        "The venue directory is temporarily unavailable."
      )
    );

    console.error("Electric Eye venues:", reason);
  }

  function initialize(raw) {
    var mount = document.getElementById(MOUNT_ID);

    if (!mount || initialized) return;

    if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
      showFailure("invalid venue dataset");
      return;
    }

    records = publicRecords(raw);

    if (!records.length) {
      showFailure("empty venue dataset");
      return;
    }

    initialized = true;
    controls = buildShell(mount);
    initializeMap();

    var scheduled = false;

    function schedule() {
      if (scheduled) return;
      scheduled = true;

      requestAnimationFrame(function () {
        scheduled = false;
        render();
      });
    }

    controls.search.addEventListener("input", schedule);
    controls.sort.addEventListener("change", render);

    controls.reset.addEventListener("click", function () {
      controls.search.value = "";
      controls.sort.value = "name";
      render();
      controls.search.focus();
    });

    addEventListener("hashchange", function () {
      highlightHashVenue(true);
    });

    render();

    setTimeout(function () {
      highlightHashVenue(true);
    }, 0);

    window.ElectricEyeVenues = Object.freeze({
      venueCount: records.length,
      mappedCount: records.filter(function (r) {
        return r.mapReady;
      }).length,
      version: "1.0.0"
    });

    document.dispatchEvent(
      new CustomEvent("ee:venues-ready", {
        detail: window.ElectricEyeVenues
      })
    );
  }

  function attempt() {
    if (initialized) return;
    if (window.ElectricEyeVenueData !== undefined) {
      initialize(window.ElectricEyeVenueData);
    }
  }

  document.addEventListener(READY, attempt);
  document.addEventListener(ERROR, function (event) {
    showFailure(event.detail && event.detail.reason);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attempt, {
      once: true
    });
  } else {
    attempt();
  }
}());
