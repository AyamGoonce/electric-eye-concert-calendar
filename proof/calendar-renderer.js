(function () {
  "use strict";
  var MOUNT_ID = "ee-concert-calendar";
  var DATA_READY_EVENT = "ee:concert-data-ready";
  var DATA_ERROR_EVENT = "ee:concert-data-error";
  var FAILURE_DELAY_MS = 4000;
  var NEW_WINDOW_MS = 72 * 60 * 60 * 1000;
  var initialized = false;
  var failureTimer = null;
  var publicGenres = Object.freeze([
    "Comedy", "Electronic", "Folk / Country", "French chanson",
    "Hip-hop / Rap", "Jazz / Blues", "Metal / Hard Rock", "Pop",
    "R&B / Soul / Funk", "Reggae / Dub / Ska", "Rock / Indie / Punk",
    "World / Latin"
  ]);
  var quickDateModes = Object.freeze(["tonight", "week", "weekend"]);

  function normalize(value) {
    return (value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
  }
  function articleAwareKey(value, overrides) {
    var normalized = normalize(value);
    return overrides[normalized] || normalized.replace(/^(?:(?:the|a|an|le|la|les)\s+|l['’]\s*)/i, "");
  }
  function venueIdentity(value) { return normalize(value).replace(/[^a-z0-9]+/g, " ").trim(); }
  function validText(value) { return typeof value === "string" && value.trim().length > 0; }
  function validStringArray(value) { return Array.isArray(value) && value.every(function (item) { return typeof item === "string"; }); }
  function validTicket(value) {
    if (value === null) return true;
    if (typeof value !== "string") return false;
    try { var url = new URL(value); return url.protocol === "http:" || url.protocol === "https:"; }
    catch (error) { return false; }
  }
  function validTimestamp(value) { return typeof value === "string" && !Number.isNaN(Date.parse(value)); }
  function validEvent(event) {
    return event && /^\d{4}-\d{2}-\d{2}$/.test(event.d) && validText(event.h) &&
      validStringArray(event.o) && validText(event.v) && validText(event.c) &&
      typeof event.g === "string" && validStringArray(event.x) && validStringArray(event.p) &&
      validTicket(event.t) && typeof event.f === "boolean" && typeof event.so === "boolean" &&
      validTimestamp(event.fs);
  }
  function showFailure(message, diagnostic) {
    var mount = document.getElementById(MOUNT_ID);
    if (!mount || initialized) return;
    window.clearTimeout(failureTimer); mount.replaceChildren();
    var notice = document.createElement("p");
    notice.className = "ee-calendar-message ee-calendar-failure"; notice.setAttribute("role", "status");
    notice.textContent = message || "The concert calendar is temporarily unavailable. Please try again later.";
    mount.append(notice); console.error("Electric Eye concert calendar:", diagnostic || "event data unavailable");
  }
  function addText(parent, className, text, tagName) {
    var element = document.createElement(tagName || "div"); element.className = className;
    element.textContent = text; parent.append(element); return element;
  }
  function addOption(select, value, label) {
    var element = document.createElement("option"); element.value = value; element.textContent = label; select.append(element);
  }
  function addSelect(filters, labelText, id, initialLabel) {
    var label = document.createElement("label"); label.htmlFor = id; label.append(document.createTextNode(labelText));
    var select = document.createElement("select"); select.id = id; addOption(select, "", initialLabel);
    label.append(select); filters.append(label); return select;
  }
  function addQuickButton(parent, value, label) {
    var button = addText(parent, "ee-calendar-quick-date", label, "button");
    button.type = "button"; button.dataset.mode = value; button.setAttribute("aria-pressed", "false"); return button;
  }
  function buildShell(mount, publishedAt) {
    mount.replaceChildren();
    var header = document.createElement("header"); header.className = "ee-calendar-header";
    addText(header, "ee-calendar-title", "Île-de-France Concert Calendar", "h1");
    addText(header, "ee-calendar-intro", "Upcoming concerts across Paris and Île-de-France.", "p");
    addText(header, "ee-calendar-updated", "Last updated: " + new Intl.DateTimeFormat("en-GB", {
      day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit",
      hourCycle: "h23", timeZone: "Europe/Paris"
    }).format(new Date(publishedAt)), "p");
    mount.append(header);
    var filters = document.createElement("section"); filters.className = "ee-calendar-filters";
    filters.setAttribute("aria-label", "Concert filters");
    var shortcuts = document.createElement("div"); shortcuts.className = "ee-calendar-shortcuts";
    shortcuts.setAttribute("aria-label", "Quick date filters");
    var tonight = addQuickButton(shortcuts, "tonight", "Tonight");
    var week = addQuickButton(shortcuts, "week", "This Week");
    var weekend = addQuickButton(shortcuts, "weekend", "This Weekend");
    var allDates = addQuickButton(shortcuts, "", "All Dates"); allDates.setAttribute("aria-pressed", "true");
    var newLabel = document.createElement("label"); newLabel.className = "ee-calendar-new-control";
    var newlyAdded = document.createElement("input"); newlyAdded.type = "checkbox"; newlyAdded.id = "ee-calendar-new";
    newLabel.append(newlyAdded, document.createTextNode("Newly added")); shortcuts.append(newLabel); filters.append(shortcuts);
    var searchLabel = document.createElement("label"); searchLabel.className = "ee-calendar-search-control";
    searchLabel.htmlFor = "ee-calendar-search"; searchLabel.append(document.createTextNode("Search"));
    var search = document.createElement("input"); search.id = "ee-calendar-search"; search.type = "search";
    search.placeholder = "Artist, opener, venue or town"; search.autocomplete = "off"; searchLabel.append(search); filters.append(searchLabel);
    var monthFilter = addSelect(filters, "Month", "ee-calendar-month", "All months");
    var venueFilter = addSelect(filters, "Venue", "ee-calendar-venue", "All venues");
    var genreFilter = addSelect(filters, "Genre", "ee-calendar-genre", "All genres");
    var sortOrder = addSelect(filters, "Sort", "ee-calendar-sort", "Date — soonest first");
    sortOrder.firstElementChild.value = "date-asc"; addOption(sortOrder, "date-desc", "Date — latest first");
    addOption(sortOrder, "artist-asc", "Headliner — A–Z"); addOption(sortOrder, "venue-asc", "Venue — A–Z");
    var clearButton = addText(filters, "ee-calendar-clear", "Clear", "button"); clearButton.type = "button"; mount.append(filters);
    var summary = document.createElement("div"); summary.className = "ee-calendar-summary";
    var count = addText(summary, "ee-calendar-result-count", "", "span"); count.setAttribute("aria-live", "polite"); mount.append(summary);
    var list = document.createElement("ol"); list.className = "ee-calendar-event-list"; mount.append(list);
    var noResults = addText(mount, "ee-calendar-message ee-calendar-no-results", "No concerts match your current filters.", "p"); noResults.hidden = true;
    return { search: search, monthFilter: monthFilter, venueFilter: venueFilter, genreFilter: genreFilter,
      sortOrder: sortOrder, clearButton: clearButton, newlyAdded: newlyAdded,
      quickButtons: [tonight, week, weekend, allDates], list: list, count: count,
      noResults: noResults, quickMode: "" };
  }
  function parisDateParts(now) {
    var values = {};
    new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Paris", year: "numeric", month: "2-digit", day: "2-digit" })
      .formatToParts(now).forEach(function (part) { values[part.type] = part.value; });
    return { year: Number(values.year), month: Number(values.month), day: Number(values.day) };
  }
  function isoFromUTCDate(value) { return value.toISOString().slice(0, 10); }
  function quickDateRange(mode, now) {
    var parts = parisDateParts(now); var current = new Date(Date.UTC(parts.year, parts.month - 1, parts.day));
    var day = current.getUTCDay(); var mondayOffset = day === 0 ? -6 : 1 - day;
    if (mode === "tonight") return [isoFromUTCDate(current), isoFromUTCDate(current)];
    if (mode === "week") {
      var monday = new Date(current); monday.setUTCDate(current.getUTCDate() + mondayOffset);
      var sunday = new Date(monday); sunday.setUTCDate(monday.getUTCDate() + 6);
      return [isoFromUTCDate(monday), isoFromUTCDate(sunday)];
    }
    if (mode === "weekend") {
      var daysUntilFriday = day === 0 ? -2 : 5 - day;
      var friday = new Date(current); friday.setUTCDate(current.getUTCDate() + daysUntilFriday);
      var sundayEnd = new Date(friday); sundayEnd.setUTCDate(friday.getUTCDate() + 2);
      return [isoFromUTCDate(friday), isoFromUTCDate(sundayEnd)];
    }
    return null;
  }
  function initialize(rawEvents) {
    var mount = document.getElementById(MOUNT_ID); var metadata = window.ElectricEyeConcertMeta;
    if (!mount || initialized) return;
    if (!Array.isArray(rawEvents) || rawEvents.length === 0 || !rawEvents.every(validEvent) || !metadata || !validTimestamp(metadata.publishedAt)) {
      showFailure(null, "malformed or empty event dataset"); return;
    }
    initialized = true; window.clearTimeout(failureTimer);
    var now = new Date(); var expanded = new Set();
    var artistSortOverrides = { "a perfect circle": "Perfect Circle", "an pierle": "An Pierlé" }; var venueSortOverrides = {};
    var events = rawEvents.map(function (source, index) {
      var event = Object.assign({}, source); event.i = index;
      event.a = articleAwareKey(event.h, artistSortOverrides); event.w = articleAwareKey(event.v, venueSortOverrides);
      event.s = normalize([event.h].concat(event.o, [event.v, event.c]).join(" "));
      event.n = now.getTime() - Date.parse(event.fs) >= 0 && now.getTime() - Date.parse(event.fs) <= NEW_WINDOW_MS; return event;
    });
    var controls = buildShell(mount, metadata.publishedAt);
    var dateFormatter = new Intl.DateTimeFormat("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
    var separatorFormatter = new Intl.DateTimeFormat("en-GB", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" });
    var monthFormatter = new Intl.DateTimeFormat("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
    var compareText = function (left, right) { return left.localeCompare(right, "fr", { sensitivity: "base" }); };
    var compareDateAscending = function (left, right) { return compareText(left.d, right.d); };
    var compareArtist = function (left, right) { return compareText(left.a, right.a) || compareDateAscending(left, right) || compareText(left.w, right.w) || left.i - right.i; };
    var compareVenue = function (left, right) { return compareText(left.w, right.w) || compareDateAscending(left, right) || compareText(left.a, right.a) || left.i - right.i; };
    var compareDate = function (left, right, direction) { return direction * compareDateAscending(left, right) || compareText(left.a, right.a) || compareText(left.w, right.w) || left.i - right.i; };
    var dateFromISO = function (value) { var parts = value.split("-").map(Number); return new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])); };
    events.forEach(function (event) { var month = event.d.slice(0, 7); if (!controls.monthFilter.querySelector('option[value="' + month + '"]')) addOption(controls.monthFilter, month, monthFormatter.format(dateFromISO(month + "-01"))); });
    var venueLabels = new Map(); events.forEach(function (event) { var identity = venueIdentity(event.v); if (!venueLabels.has(identity)) venueLabels.set(identity, event.v); });
    Array.from(venueLabels.values()).sort(function (left, right) { return compareText(articleAwareKey(left, venueSortOverrides), articleAwareKey(right, venueSortOverrides)); })
      .forEach(function (venue) { addOption(controls.venueFilter, venue, venue); });
    publicGenres.forEach(function (genre) { addOption(controls.genreFilter, genre, genre); });
    function updateQuickButtons() { controls.quickButtons.forEach(function (button) { button.setAttribute("aria-pressed", String(button.dataset.mode === controls.quickMode)); }); }
    function readURLState() {
      var params = new URLSearchParams(window.location.search); controls.search.value = params.get("q") || "";
      controls.venueFilter.value = params.get("venue") || "";
      controls.genreFilter.value = publicGenres.includes(params.get("genre")) ? params.get("genre") : "";
      controls.sortOrder.value = ["date-asc", "date-desc", "artist-asc", "venue-asc"].includes(params.get("sort")) ? params.get("sort") : "date-asc";
      controls.quickMode = quickDateModes.includes(params.get("when")) ? params.get("when") : "";
      controls.monthFilter.value = controls.quickMode ? "" : (params.get("month") || "");
      controls.newlyAdded.checked = params.get("new") === "1"; updateQuickButtons();
    }
    function updateURL(push) {
      var params = new URLSearchParams(); if (controls.search.value.trim()) params.set("q", controls.search.value.trim());
      if (controls.venueFilter.value) params.set("venue", controls.venueFilter.value); if (controls.genreFilter.value) params.set("genre", controls.genreFilter.value);
      if (controls.monthFilter.value) params.set("month", controls.monthFilter.value); if (controls.quickMode) params.set("when", controls.quickMode);
      if (controls.newlyAdded.checked) params.set("new", "1"); if (controls.sortOrder.value !== "date-asc") params.set("sort", controls.sortOrder.value);
      var url = window.location.pathname + (params.toString() ? "?" + params.toString() : "") + window.location.hash;
      window.history[push ? "pushState" : "replaceState"]({}, "", url);
    }
    function artistButton(name) {
      var container = document.createDocumentFragment(); var button = addText(container, "ee-calendar-text-button ee-calendar-artist-button", name, "button");
      button.type = "button"; button.addEventListener("click", function () { controls.search.value = name; updateURL(true); render(); controls.search.focus(); }); return button;
    }
    function createRow(event) {
      var item = document.createElement("li"); var article = document.createElement("article"); article.className = "ee-calendar-event-row";
      var eventDate = addText(article, "ee-calendar-event-date", dateFormatter.format(dateFromISO(event.d)), "time"); eventDate.dateTime = event.d;
      var artist = document.createElement("div"); artist.className = "ee-calendar-event-artist"; var heading = document.createElement("h2");
      heading.append(artistButton(event.h)); if (event.n) addText(heading, "ee-calendar-new-badge", "NEW", "span"); artist.append(heading);
      if (event.o.length) {
        var openers = document.createElement("p"); openers.className = "ee-calendar-openers"; openers.append(document.createTextNode("with "));
        var visibleCount = event.f && !expanded.has(event.i) ? Math.min(5, event.o.length) : event.o.length;
        event.o.slice(0, visibleCount).forEach(function (name, index) { if (index) openers.append(document.createTextNode(", ")); openers.append(artistButton(name)); });
        artist.append(openers);
        if (event.f && event.o.length > 5) {
          var more = addText(artist, "ee-calendar-lineup-toggle", expanded.has(event.i) ? "Show fewer" : "+ " + (event.o.length - 5) + " more artists", "button");
          more.type = "button"; more.setAttribute("aria-expanded", String(expanded.has(event.i)));
          more.addEventListener("click", function () { if (expanded.has(event.i)) expanded.delete(event.i); else expanded.add(event.i); render(); });
        }
      }
      article.append(artist);
      var venue = addText(article, "ee-calendar-text-button ee-calendar-venue", event.c.toLocaleLowerCase() === "paris" ? event.v : event.v + " (" + event.c + ")", "button");
      venue.type = "button"; venue.addEventListener("click", function () { controls.venueFilter.value = event.v; updateURL(true); render(); controls.venueFilter.focus(); });
      var metadataArea = document.createElement("div"); metadataArea.className = "ee-calendar-metadata";
      if (event.x.length) addText(metadataArea, "ee-calendar-genre", event.x[0], "span"); article.append(metadataArea);
      if (event.so) addText(article, "ee-calendar-sold-out", "SOLD OUT", "span");
      else if (event.t) { var ticket = addText(article, "ee-calendar-ticket", "Tickets", "a"); ticket.href = event.t; ticket.target = "_blank"; ticket.rel = "noopener noreferrer"; ticket.setAttribute("aria-label", "Tickets for " + event.h); }
      else addText(article, "ee-calendar-ticket-space", ""); item.append(article); return item;
    }
    function createSeparator(value) { var item = document.createElement("li"); item.className = "ee-calendar-day-separator"; item.textContent = separatorFormatter.format(dateFromISO(value)); return item; }
    function render() {
      var query = normalize(controls.search.value.trim()); var month = controls.monthFilter.value; var venue = controls.venueFilter.value;
      var genre = controls.genreFilter.value; var order = controls.sortOrder.value; var range = quickDateRange(controls.quickMode, now);
      var filtered = events.filter(function (event) { return (!query || event.s.includes(query)) && (!month || event.d.startsWith(month)) &&
        (!range || (event.d >= range[0] && event.d <= range[1])) && (!venue || venueIdentity(event.v) === venueIdentity(venue)) &&
        (!genre || event.x.includes(genre)) && (!controls.newlyAdded.checked || event.n); });
      filtered.sort(order === "date-desc" ? function (left, right) { return compareDate(left, right, -1); } : order === "artist-asc" ? compareArtist :
        order === "venue-asc" ? compareVenue : function (left, right) { return compareDate(left, right, 1); });
      var fragment = document.createDocumentFragment(); var previousDate = null;
      filtered.forEach(function (event) { if ((order === "date-asc" || order === "date-desc") && event.d !== previousDate) fragment.append(createSeparator(event.d)); fragment.append(createRow(event)); previousDate = event.d; });
      controls.list.replaceChildren(fragment); controls.count.textContent = filtered.length.toLocaleString("en-GB") + (filtered.length === 1 ? " concert" : " concerts");
      controls.list.hidden = filtered.length === 0; controls.noResults.hidden = filtered.length !== 0;
    }
    var scheduled = false;
    function scheduleRender() { if (scheduled) return; scheduled = true; window.requestAnimationFrame(function () { scheduled = false; updateURL(false); render(); }); }
    controls.search.addEventListener("input", scheduleRender);
    [controls.venueFilter, controls.genreFilter, controls.sortOrder, controls.newlyAdded].forEach(function (control) { control.addEventListener("change", function () { updateURL(true); render(); }); });
    controls.monthFilter.addEventListener("change", function () { if (controls.monthFilter.value) controls.quickMode = ""; updateQuickButtons(); updateURL(true); render(); });
    controls.quickButtons.forEach(function (button) { button.addEventListener("click", function () { controls.quickMode = button.dataset.mode; controls.monthFilter.value = ""; updateQuickButtons(); updateURL(true); render(); }); });
    controls.clearButton.addEventListener("click", function () { controls.search.value = ""; controls.monthFilter.value = ""; controls.venueFilter.value = ""; controls.genreFilter.value = ""; controls.sortOrder.value = "date-asc"; controls.newlyAdded.checked = false; controls.quickMode = ""; updateQuickButtons(); updateURL(true); render(); controls.search.focus(); });
    window.addEventListener("popstate", function () { readURLState(); render(); }); readURLState(); render();
    window.ElectricEyeConcertCalendar = Object.freeze({ eventCount: events.length, version: "2.0.0" });
    document.dispatchEvent(new CustomEvent("ee:concert-calendar-ready", { detail: window.ElectricEyeConcertCalendar }));
  }
  function attemptInitialize() { if (!document.getElementById(MOUNT_ID) || initialized) return; if (window.ElectricEyeConcertData !== undefined) initialize(window.ElectricEyeConcertData); }
  function start() { if (!document.getElementById(MOUNT_ID)) return; attemptInitialize(); if (!initialized) failureTimer = window.setTimeout(function () { showFailure(null, "timed out waiting for event data"); }, FAILURE_DELAY_MS); }
  document.addEventListener(DATA_READY_EVENT, attemptInitialize);
  document.addEventListener(DATA_ERROR_EVENT, function (event) { showFailure(null, event.detail && event.detail.reason); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true }); else start();
}());
