(function () {
  "use strict";

  var calendarUrl =
    "https://www.electriceyerock.com/p/paris-area-concert-calendar.html";

  var articleHeadings = {
    concert_review: "Concert Reviews",
    interview: "Interviews",
    album_review: "Album Reviews",
    news: "News",
    playlist: "Playlists",
    other: "More from Electric Eye"
  };

  function text(parent, tag, value, cls) {
    var node = document.createElement(tag);
    node.textContent = value;
    if (cls) node.className = cls;
    parent.append(node);
    return node;
  }

  function humanDate(value) {
    return new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC"
    }).format(new Date(value + "T12:00:00Z"));
  }

  function slugify(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase()
      .replace(/['’]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function normalize(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase()
      .replace(/['’]/g, "'")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function uniqueArticles(ids, index) {
    var seen = Object.create(null);
    var articles = [];

    ids.forEach(function (id) {
      var article = index.articles[id];
      if (!article || seen[id]) return;
      seen[id] = true;
      articles.push(article);
    });

    return articles;
  }

  function render() {
    var mount = document.getElementById("ee-genre-results");
    var genreData = window.ElectricEyeGenreData;
    var contentIndex = window.ElectricEyeContentIndex;

    if (
      !mount ||
      !genreData ||
      !contentIndex ||
      mount.dataset.ready
    ) {
      return;
    }

    var routeSlug =
      new URLSearchParams(location.search).get("genre") ||
      (location.pathname.match(/\/genre\/([^/]+)\/?$/) || [])[1] ||
      "";

    routeSlug = decodeURIComponent(routeSlug);

    var genre = (genreData.genres || []).find(function (record) {
      return slugify(record.name) === routeSlug;
    });

    if (!genre) {
      mount.dataset.ready = "1";
      text(
        mount,
        "p",
        "No Electric Eye genre coverage was found.",
        "ee-artist-empty"
      );
      return;
    }

    mount.dataset.ready = "1";

    text(mount, "p", "Electric Eye", "ee-page-kicker");
    text(mount, "h1", genre.name, "ee-artist-title");

    var artistLookup = Object.create(null);

    Object.keys(contentIndex.artists || {}).forEach(function (slug) {
      var artist = contentIndex.artists[slug];
      artistLookup[normalize(artist.n)] = {
        slug: slug,
        artist: artist
      };
    });

    var matchedArtists = [];
    var articleIds = [];
    var routeLookup =
      (window.ElectricEyeArtistLookup &&
        window.ElectricEyeArtistLookup.terms) ||
      {};

    (genre.artists || []).forEach(function (name) {
      var match = artistLookup[normalize(name)];
      var routeSlug = routeLookup[name];

      if (!routeSlug) return;

      matchedArtists.push({
        name: name,
        slug: routeSlug,
        artist: match ? match.artist : null
      });

      if (match) {
        (match.artist.ar || []).forEach(function (id) {
          articleIds.push(id);
        });
      }
    });

    var visibleArtistCount = matchedArtists.length;
    var context = visibleArtistCount + " artist";
    if (visibleArtistCount !== 1) context += "s";

    if (genre.parent) {
      context += " · " + genre.parent + " subgenre";
    }

    text(
      mount,
      "p",
      context,
      "ee-page-context"
    );

    if (matchedArtists.length) {
      var artistsSection = document.createElement("section");
      text(artistsSection, "h2", "Artists");

      var artistList = document.createElement("ul");

      matchedArtists
        .slice()
        .sort(function (a, b) {
          return a.name.localeCompare(b.name);
        })
        .forEach(function (entry) {
          var item = document.createElement("li");
          item.className = "ee-article-card";

          if (entry.slug) {
            var link = document.createElement("a");
            link.href =
              "https://archive.electriceyerock.com/artist/" +
              encodeURIComponent(entry.slug) +
              "/";
            link.textContent = entry.name;
            item.append(link);
          } else {
            text(item, "span", entry.name);
          }

          artistList.append(item);
        });

      artistsSection.append(artistList);
      mount.append(artistsSection);
    }

    var articles = uniqueArticles(articleIds, contentIndex);
    var groups = {};

    articles.forEach(function (article) {
      (groups[article.y] || (groups[article.y] = [])).push(article);
    });

    Object.keys(articleHeadings).forEach(function (kind) {
      if (!groups[kind]) return;

      var section = document.createElement("section");
      text(section, "h2", articleHeadings[kind]);

      var list = document.createElement("ul");

      groups[kind]
        .sort(function (a, b) {
          return b.d.localeCompare(a.d);
        })
        .forEach(function (article) {
          var item = document.createElement("li");
          item.className = "ee-article-card";

          if (article.im) {
            var image = document.createElement("img");
            image.src = article.im;
            image.alt = "";
            image.loading = "lazy";
            image.decoding = "async";
            image.width = 96;
            image.height = 72;
            item.append(image);
          }

          var copy = document.createElement("div");
          var link = document.createElement("a");

          link.href = article.u;
          link.textContent = article.t;
          copy.append(link);

          var time = document.createElement("time");
          time.dateTime = article.d;
          time.textContent = humanDate(article.d);
          copy.append(time);

          item.append(copy);
          list.append(item);
        });

      section.append(list);
      mount.append(section);
    });

    var genreArtistNames = Object.create(null);

    (genre.artists || []).forEach(function (name) {
      genreArtistNames[normalize(name)] = true;
    });

    var events = (window.ElectricEyeConcertData || []).filter(
      function (event) {
        var names = [event.h]
          .concat(event.ch || [])
          .concat(event.o || []);

        return names.some(function (name) {
          return genreArtistNames[normalize(name)];
        });
      }
    );

    if (events.length) {
      var concertSection = document.createElement("section");
      text(concertSection, "h2", "Upcoming Concerts");

      var concertList = document.createElement("ul");

      events
        .slice()
        .sort(function (a, b) {
          return a.d.localeCompare(b.d);
        })
        .forEach(function (event) {
          var item = document.createElement("li");
          item.className = "ee-article-card";

          var link = document.createElement("a");
          link.href = calendarUrl + "#event-" + event.i;
          link.textContent =
            humanDate(event.d) +
            " — " +
            event.h +
            " — " +
            event.v;

          item.append(link);
          concertList.append(item);
        });

      concertSection.append(concertList);
      mount.append(concertSection);
    }
  }

  document.addEventListener("DOMContentLoaded", render);
  document.addEventListener("ee:genre-data-ready", render);
  document.addEventListener("ee:content-index-ready", render);
  document.addEventListener("ee:concert-data-ready", render);

  render();
}());
