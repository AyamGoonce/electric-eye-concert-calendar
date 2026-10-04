(function () {
  "use strict";

  var calendarUrl =
    "https://www.electriceyerock.com/p/paris-area-concert-calendar.html";

  var headings = {
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

  function eventNames(event) {
    return [event.h]
      .concat(event.ch || [])
      .concat(event.o || []);
  }

  function findGenreArtistName(slug, genreData) {
    var found = "";

    (genreData && genreData.genres || []).some(function (genre) {
      return (genre.artists || []).some(function (name) {
        if (slugify(name) === slug) {
          found = name;
          return true;
        }
        return false;
      });
    });

    return found;
  }

  function findCalendarArtistName(slug, events) {
    var found = "";

    events.some(function (event) {
      return eventNames(event).some(function (name) {
        if (slugify(name) === slug) {
          found = name;
          return true;
        }
        return false;
      });
    });

    return found;
  }

  function render() {
    var mount = document.getElementById("ee-artist-results");
    var index = window.ElectricEyeContentIndex;
    var events = window.ElectricEyeConcertData || [];
    var genreData = window.ElectricEyeGenreData;

    if (
      !mount ||
      !index ||
      !genreData ||
      mount.dataset.ready
    ) {
      return;
    }

    var slug =
      new URLSearchParams(location.search).get("artist") ||
      (location.pathname.match(/\/artist\/([^/]+)\/?$/) || [])[1] ||
      "";

    slug = decodeURIComponent(slug);

    var artist = index.artists[slug] || null;

    var artistName =
      (artist && artist.n) ||
      findGenreArtistName(slug, genreData) ||
      findCalendarArtistName(slug, events);

    var matchedEvents = events.filter(function (event) {
      var linkedThroughCoverage = (event.ee || []).some(function (link) {
        return link.slug === slug;
      });

      var linkedThroughBill = eventNames(event).some(function (name) {
        return slugify(name) === slug;
      });

      return linkedThroughCoverage || linkedThroughBill;
    });

    if (!artistName) {
      mount.dataset.ready = "1";
      text(
        mount,
        "p",
        "No Electric Eye artist record was found.",
        "ee-artist-empty"
      );
      return;
    }

    mount.dataset.ready = "1";

    var home=document.createElement("a");home.href="https://www.electriceyerock.com/p/welcome-to-electric-eye.html";home.textContent="Electric Eye";home.className="ee-page-kicker ee-home-link";mount.append(home);
    text(mount, "h1", artistName, "ee-artist-title");

    var articleIds = artist ? (artist.ar || []) : [];

    if (articleIds.length) {
      text(
        mount,
        "p",
        "Reviews, interviews, news and archive coverage.",
        "ee-page-context"
      );
    } else if (matchedEvents.length) {
      text(
        mount,
        "p",
        "Concert dates and Electric Eye archive connections.",
        "ee-page-context"
      );
    } else {
      text(
        mount,
        "p",
        "Electric Eye artist archive.",
        "ee-page-context"
      );
    }

    if (artist && artist.os) {
      var actions = document.createElement("div");
      actions.className = "ee-page-actions";

      var official = document.createElement("a");
      official.href = artist.os;
      official.target = "_blank";
      official.rel = "noopener noreferrer";
      official.textContent = "Official Site";

      actions.append(official);
      mount.append(actions);
    }

    if (articleIds.length) {
      var groups = {};

      articleIds
        .map(function (id) {
          return index.articles[id];
        })
        .filter(Boolean)
        .forEach(function (article) {
          (groups[article.y] || (groups[article.y] = [])).push(article);
        });

      Object.keys(headings).forEach(function (kind) {
        if (!groups[kind]) return;

        var section = document.createElement("section");
        text(section, "h2", headings[kind]);

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
    }

    if (matchedEvents.length) {
      var concertSection = document.createElement("section");
      text(concertSection, "h2", "Upcoming Concerts");

      var concertList = document.createElement("ul");

      matchedEvents
        .slice()
        .sort(function (a, b) {
          return a.d.localeCompare(b.d);
        })
        .forEach(function (event) {
          var item = document.createElement("li");
          item.className = "ee-article-card";

          var link = document.createElement("a");
          link.href = calendarUrl+"#event-"+event.i;
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
  document.addEventListener("ee:content-index-ready", render);
  document.addEventListener("ee:concert-data-ready", render);
  document.addEventListener("ee:genre-data-ready", render);

  render();
}());
