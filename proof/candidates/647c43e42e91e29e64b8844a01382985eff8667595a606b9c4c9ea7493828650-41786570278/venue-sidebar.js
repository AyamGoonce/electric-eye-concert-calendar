(function () {
  "use strict";

  var READY_EVENT = "ee:venue-data-ready";
  var initialized = false;
  var sidebarMap = null;

  function clean(value) {
    return String(value || "")
      .replace(/\u00a0/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalizeUrl(value) {
    try {
      var url = new URL(value, window.location.origin);

      if (/blogspot\./i.test(url.hostname)) {
        url = new URL(url.pathname + url.search, window.location.origin);
      }

      return (
        url.origin +
        url.pathname.replace(/\/$/, "")
      );
    } catch (error) {
      return clean(value)
        .replace(/[?#].*$/, "")
        .replace(/\/$/, "");
    }
  }

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

  function venueHref(record) {
    return "/p/venues.html#venue-" + slug(record.name);
  }

  function currentVenue(raw) {
    var current = normalizeUrl(window.location.href);
    var names = Object.keys(raw || {});

    for (var i = 0; i < names.length; i++) {
      var source = raw[names[i]] || {};
      var articles = Array.isArray(source.articles)
        ? source.articles
        : [];

      for (var j = 0; j < articles.length; j++) {
        if (
          articles[j] &&
          articles[j].url &&
          normalizeUrl(articles[j].url) === current
        ) {
          return {
            name: source.name || names[i],
            address: source.address || "",
            city: source.city || "",
            lat: source.lat,
            lng: source.lng,
            mapReady: source.mapReady === true
          };
        }
      }
    }

    return null;
  }

  function element(tag, className, text) {
    var node = document.createElement(tag);

    if (className) {
      node.className = className;
    }

    if (text !== undefined && text !== null) {
      node.textContent = text;
    }

    return node;
  }

  function popupContent(record) {
    var box = element("div", "ee-sb-venue-popup");

    box.appendChild(
      element("strong", "", record.name)
    );

    var location = [record.address, record.city]
      .filter(Boolean)
      .join(" · ");

    if (location) {
      box.appendChild(
        element("div", "ee-sb-venue-popup-location", location)
      );
    }

    var link = element("a", "", "View venue →");
    link.href = venueHref(record);
    box.appendChild(link);

    return box;
  }

  function createMap(frame, record) {
    if (
      !window.L ||
      !record.mapReady ||
      typeof record.lat !== "number" ||
      typeof record.lng !== "number"
    ) {
      return;
    }

    sidebarMap = L.map(frame, {
      scrollWheelZoom: false,
      dragging: true,
      zoomControl: true,
      attributionControl: true
    }).setView([record.lat, record.lng], 15);

    L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
      }
    ).addTo(sidebarMap);

    L.marker([record.lat, record.lng])
      .addTo(sidebarMap)
      .bindPopup(popupContent(record));

    setTimeout(function () {
      sidebarMap.invalidateSize();
    }, 0);
  }

  function render(record) {
    var root = document.getElementById("ee-sb-root");

    if (!root) {
      return;
    }

    var calendar = root.querySelector(".ee-sb-agenda");

    if (!calendar) {
      return;
    }

    if (document.getElementById("ee-sb-venue-map")) {
      return;
    }

    var section = element(
      "section",
      "ee-sb-module ee-sb-venue-map"
    );

    section.id = "ee-sb-venue-map";
    section.setAttribute(
      "aria-labelledby",
      "ee-sb-venue-map-heading"
    );

    var heading = element("div", "ee-sb-heading");

    var h2 = element(
      "h2",
      "",
      "Venue"
    );

    h2.id = "ee-sb-venue-map-heading";

    var allVenues = element(
      "a",
      "",
      "All venues"
    );

    allVenues.href = "/p/venues.html";

    heading.appendChild(h2);
    heading.appendChild(allVenues);
    section.appendChild(heading);

    var venueLink = element(
      "a",
      "ee-sb-venue-map-name",
      record.name
    );

    venueLink.href = venueHref(record);

    section.appendChild(venueLink);

    if (
      record.mapReady &&
      typeof record.lat === "number" &&
      typeof record.lng === "number"
    ) {
      var frame = element(
        "div",
        "ee-sb-venue-map-frame"
      );

      frame.setAttribute(
        "aria-label",
        "Map showing " + record.name
      );

      section.appendChild(frame);
      calendar.parentNode.insertBefore(section, calendar);

      createMap(frame, record);
    } else {
      calendar.parentNode.insertBefore(section, calendar);
    }
  }

  function initialize(raw) {
    if (initialized) {
      return;
    }

    if (
      !raw ||
      typeof raw !== "object" ||
      Array.isArray(raw)
    ) {
      return;
    }

    var record = currentVenue(raw);

    if (!record) {
      return;
    }

    initialized = true;
    render(record);
  }

  function attempt() {
    if (initialized) {
      return;
    }

    if (window.ElectricEyeVenueData !== undefined) {
      initialize(window.ElectricEyeVenueData);
    }
  }

  document.addEventListener(
    READY_EVENT,
    attempt
  );

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      attempt,
      { once: true }
    );
  } else {
    attempt();
  }
}());
