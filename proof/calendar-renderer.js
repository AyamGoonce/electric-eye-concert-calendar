(function () {
  "use strict";

  var MOUNT_ID = "ee-concert-calendar";
  var DATA_READY_EVENT = "ee:concert-data-ready";
  var DATA_ERROR_EVENT = "ee:concert-data-error";
  var FAILURE_DELAY_MS = 4000;
  var initialized = false;
  var failureTimer = null;

  function normalize(value) {
    return (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase();
  }

  function articleAwareKey(value, overrides) {
    var normalized = normalize(value);
    return overrides[normalized] || normalized.replace(/^(?:(?:the|le|la|les)\s+|l['’]\s*)/i, "");
  }

  function validText(value) {
    return typeof value === "string" && value.trim().length > 0;
  }

  function validStringArray(value) {
    return Array.isArray(value) && value.every(function (item) { return typeof item === "string"; });
  }

  function validTicket(value) {
    if (value === null) return true;
    if (typeof value !== "string") return false;
    try {
      var url = new URL(value);
      return url.protocol === "http:" || url.protocol === "https:";
    } catch (error) {
      return false;
    }
  }

  function validEvent(event) {
    return event &&
      /^\d{4}-\d{2}-\d{2}$/.test(event.d) &&
      validText(event.h) &&
      validStringArray(event.o) &&
      validText(event.v) &&
      validText(event.c) &&
      typeof event.g === "string" &&
      validStringArray(event.x) &&
      validStringArray(event.p) &&
      validTicket(event.t);
  }

  function showFailure(message, diagnostic) {
    var mount = document.getElementById(MOUNT_ID);
    if (!mount || initialized) return;
    window.clearTimeout(failureTimer);
    mount.replaceChildren();
    var notice = document.createElement("p");
    notice.className = "ee-calendar-message ee-calendar-failure";
    notice.setAttribute("role", "status");
    notice.textContent = message || "The concert calendar is temporarily unavailable. Please try again later.";
    mount.append(notice);
    console.error("Electric Eye concert calendar:", diagnostic || "event data unavailable");
  }

  function addText(parent, className, text, tagName) {
    var element = document.createElement(tagName || "div");
    element.className = className;
    element.textContent = text;
    parent.append(element);
    return element;
  }

  function addOption(select, value, label) {
    var element = document.createElement("option");
    element.value = value;
    element.textContent = label;
    select.append(element);
  }

  function addSelect(filters, labelText, id, initialLabel) {
    var label = document.createElement("label");
    label.htmlFor = id;
    label.append(document.createTextNode(labelText));
    var select = document.createElement("select");
    select.id = id;
    addOption(select, "", initialLabel);
    label.append(select);
    filters.append(label);
    return select;
  }

  function buildShell(mount) {
    mount.replaceChildren();

    var header = document.createElement("header");
    header.className = "ee-calendar-header";
    addText(header, "ee-calendar-title", "Île-de-France Concert Calendar", "h1");
    addText(header, "ee-calendar-intro", "Upcoming concerts across Paris and Île-de-France.", "p");
    mount.append(header);

    var filters = document.createElement("section");
    filters.className = "ee-calendar-filters";
    filters.setAttribute("aria-label", "Concert filters");

    var searchLabel = document.createElement("label");
    searchLabel.className = "ee-calendar-search-control";
    searchLabel.htmlFor = "ee-calendar-search";
    searchLabel.append(document.createTextNode("Search"));
    var search = document.createElement("input");
    search.id = "ee-calendar-search";
    search.type = "search";
    search.placeholder = "Artist, opener, venue or town";
    search.autocomplete = "off";
    searchLabel.append(search);
    filters.append(searchLabel);

    var monthFilter = addSelect(filters, "Date", "ee-calendar-month", "All dates");
    var venueFilter = addSelect(filters, "Venue", "ee-calendar-venue", "All venues");
    var genreFilter = addSelect(filters, "Genre", "ee-calendar-genre", "All genres");
    var sortOrder = addSelect(filters, "Sort", "ee-calendar-sort", "Date — soonest first");
    sortOrder.firstElementChild.value = "date-asc";
    addOption(sortOrder, "date-desc", "Date — latest first");
    addOption(sortOrder, "artist-asc", "Artist — A–Z");
    addOption(sortOrder, "venue-asc", "Venue — A–Z");

    var clearButton = addText(filters, "ee-calendar-clear", "Clear", "button");
    clearButton.type = "button";
    mount.append(filters);

    var summary = document.createElement("div");
    summary.className = "ee-calendar-summary";
    var count = addText(summary, "ee-calendar-result-count", "", "span");
    count.setAttribute("aria-live", "polite");
    mount.append(summary);

    var list = document.createElement("ol");
    list.className = "ee-calendar-event-list";
    mount.append(list);

    var noResults = addText(mount, "ee-calendar-message ee-calendar-no-results", "No concerts match your current filters.", "p");
    noResults.hidden = true;

    return {
      search: search,
      monthFilter: monthFilter,
      venueFilter: venueFilter,
      genreFilter: genreFilter,
      sortOrder: sortOrder,
      clearButton: clearButton,
      list: list,
      count: count,
      noResults: noResults
    };
  }

  function initialize(rawEvents) {
    var mount = document.getElementById(MOUNT_ID);
    if (!mount || initialized) return;

    if (!Array.isArray(rawEvents) || rawEvents.length === 0 || !rawEvents.every(validEvent)) {
      showFailure(null, "malformed or empty event dataset");
      return;
    }

    initialized = true;
    window.clearTimeout(failureTimer);

    var artistSortOverrides = { "a perfect circle": "Perfect Circle" };
    var venueSortOverrides = {};
    var events = rawEvents.map(function (source, index) {
      var event = Object.assign({}, source);
      event.i = index;
      event.a = articleAwareKey(event.h, artistSortOverrides);
      event.w = articleAwareKey(event.v, venueSortOverrides);
      event.s = normalize([event.h].concat(event.o, [event.v, event.c]).join(" "));
      return event;
    });
    var controls = buildShell(mount);
    var dateFormatter = new Intl.DateTimeFormat("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
    var monthFormatter = new Intl.DateTimeFormat("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
    var compareText = function (left, right) { return left.localeCompare(right, "fr", { sensitivity: "base" }); };
    var compareDateAscending = function (left, right) { return compareText(left.d, right.d); };
    var compareArtist = function (left, right) { return compareText(left.a, right.a) || compareDateAscending(left, right) || compareText(left.w, right.w) || left.i - right.i; };
    var compareVenue = function (left, right) { return compareText(left.w, right.w) || compareDateAscending(left, right) || compareText(left.a, right.a) || left.i - right.i; };
    var compareDate = function (left, right, direction) { return direction * compareDateAscending(left, right) || compareText(left.a, right.a) || compareText(left.w, right.w) || left.i - right.i; };
    var dateFromISO = function (value) {
      var parts = value.split("-").map(Number);
      return new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    };

    events.forEach(function (event) {
      var month = event.d.slice(0, 7);
      if (!controls.monthFilter.querySelector('option[value="' + month + '"]')) {
        addOption(controls.monthFilter, month, monthFormatter.format(dateFromISO(month + "-01")));
      }
    });
    Array.from(new Set(events.map(function (event) { return event.v; })))
      .sort(function (left, right) { return left.localeCompare(right, "fr", { sensitivity: "base" }); })
      .forEach(function (venue) { addOption(controls.venueFilter, venue, venue); });
    Array.from(new Set(events.flatMap(function (event) { return event.x; })))
      .sort()
      .forEach(function (genre) { addOption(controls.genreFilter, genre, genre); });

    function createRow(event) {
      var item = document.createElement("li");
      var article = document.createElement("article");
      article.className = "ee-calendar-event-row";
      var eventDate = addText(article, "ee-calendar-event-date", dateFormatter.format(dateFromISO(event.d)), "time");
      eventDate.dateTime = event.d;
      var artist = document.createElement("div");
      artist.className = "ee-calendar-event-artist";
      addText(artist, "", event.h, "h2");
      if (event.o.length) addText(artist, "ee-calendar-openers", "with " + event.o.join(", "), "p");
      article.append(artist);
      addText(article, "ee-calendar-venue", event.c.toLocaleLowerCase() === "paris" ? event.v : event.v + " (" + event.c + ")");
      var metadata = document.createElement("div");
      metadata.className = "ee-calendar-metadata";
      if (event.g) addText(metadata, "ee-calendar-genre", event.g, "span");
      if (event.p.length) addText(metadata, "ee-calendar-promoter", event.p.join(", "), "span");
      article.append(metadata);
      if (event.t) {
        var ticket = addText(article, "ee-calendar-ticket", "Tickets", "a");
        ticket.href = event.t;
        ticket.target = "_blank";
        ticket.rel = "noopener noreferrer";
        ticket.setAttribute("aria-label", "Tickets for " + event.h);
      } else {
        addText(article, "ee-calendar-ticket-space", "");
      }
      item.append(article);
      return item;
    }

    function render() {
      var query = normalize(controls.search.value.trim());
      var month = controls.monthFilter.value;
      var venue = controls.venueFilter.value;
      var genre = controls.genreFilter.value;
      var order = controls.sortOrder.value;
      var filtered = events.filter(function (event) {
        return (!query || event.s.includes(query)) &&
          (!month || event.d.startsWith(month)) &&
          (!venue || event.v === venue) &&
          (!genre || event.x.includes(genre));
      });
      filtered.sort(
        order === "date-desc" ? function (left, right) { return compareDate(left, right, -1); } :
        order === "artist-asc" ? compareArtist :
        order === "venue-asc" ? compareVenue :
        function (left, right) { return compareDate(left, right, 1); }
      );
      var fragment = document.createDocumentFragment();
      filtered.forEach(function (event) { fragment.append(createRow(event)); });
      controls.list.replaceChildren(fragment);
      controls.count.textContent = filtered.length.toLocaleString("en-GB") + (filtered.length === 1 ? " concert" : " concerts");
      controls.list.hidden = filtered.length === 0;
      controls.noResults.hidden = filtered.length !== 0;
    }

    var scheduled = false;
    function scheduleRender() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(function () {
        scheduled = false;
        render();
      });
    }

    controls.search.addEventListener("input", scheduleRender);
    [controls.monthFilter, controls.venueFilter, controls.genreFilter, controls.sortOrder]
      .forEach(function (control) { control.addEventListener("change", scheduleRender); });
    controls.clearButton.addEventListener("click", function () {
      controls.search.value = "";
      controls.monthFilter.value = "";
      controls.venueFilter.value = "";
      controls.genreFilter.value = "";
      render();
      controls.search.focus();
    });
    render();

    window.ElectricEyeConcertCalendar = Object.freeze({
      eventCount: events.length,
      version: "1.0.0"
    });
    document.dispatchEvent(new CustomEvent("ee:concert-calendar-ready", { detail: window.ElectricEyeConcertCalendar }));
  }

  function attemptInitialize() {
    if (!document.getElementById(MOUNT_ID) || initialized) return;
    if (window.ElectricEyeConcertData !== undefined) initialize(window.ElectricEyeConcertData);
  }

  function start() {
    if (!document.getElementById(MOUNT_ID)) return;
    attemptInitialize();
    if (!initialized) {
      failureTimer = window.setTimeout(function () {
        showFailure(null, "timed out waiting for event data");
      }, FAILURE_DELAY_MS);
    }
  }

  document.addEventListener(DATA_READY_EVENT, attemptInitialize);
  document.addEventListener(DATA_ERROR_EVENT, function (event) {
    showFailure(null, event.detail && event.detail.reason);
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
}());
