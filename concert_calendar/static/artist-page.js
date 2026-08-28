(function () {
  "use strict";
  var mountId = "ee-artist-results";
  var calendarUrl = "https://www.electriceyerock.com/p/paris-area-concert-calendar.html";
  var headings = {
    concert_review: "Concert Reviews", interview: "Interviews",
    album_review: "Album Reviews", news: "News", playlist: "Playlists",
    other: "Other Coverage"
  };
  function text(parent, tag, value, cls) {
    var node = document.createElement(tag); node.textContent = value;
    if (cls) node.className = cls; parent.append(node); return node;
  }
  function render() {
    var mount = document.getElementById(mountId), index = window.ElectricEyeContentIndex;
    if (!mount || !index || mount.dataset.ready) return;
    mount.dataset.ready = "1";
    var slug = new URLSearchParams(location.search).get("artist") || "";
    var artist = index.artists[slug];
    if (!artist) { text(mount, "p", "No Electric Eye artist coverage was found.", "ee-artist-empty"); return; }
    text(mount, "h1", artist.n, "ee-artist-title");
    var groups = {};
    artist.ar.map(function (id) { return index.articles[id]; }).forEach(function (article) {
      (groups[article.y] || (groups[article.y] = [])).push(article);
    });
    Object.keys(headings).forEach(function (kind) {
      if (!groups[kind]) return;
      var section = document.createElement("section");
      text(section, "h2", headings[kind]);
      var list = document.createElement("ul");
      groups[kind].sort(function (a, b) { return b.d.localeCompare(a.d); }).forEach(function (article) {
        var item = document.createElement("li"), link = document.createElement("a");
        link.href = article.u; link.textContent = article.t;
        var time = document.createElement("time"); time.dateTime = article.d; time.textContent = article.d;
        item.append(link, time); list.append(item);
      });
      section.append(list); mount.append(section);
    });
    var events = (window.ElectricEyeConcertData || []).filter(function (event) {
      return (event.ee || []).some(function (link) { return link.slug === slug; });
    });
    if (events.length) {
      var section = document.createElement("section"); text(section, "h2", "Upcoming Concerts");
      var list = document.createElement("ul");
      events.forEach(function (event) {
        var item = document.createElement("li"), link = document.createElement("a");
        link.href = calendarUrl + "#event-" + event.i;
        link.textContent = event.d + " — " + event.h + " — " + event.v;
        item.append(link); list.append(item);
      });
      section.append(list); mount.append(section);
    }
  }
  document.addEventListener("DOMContentLoaded", render);
  document.addEventListener("ee:content-index-ready", render);
  document.addEventListener("ee:concert-data-ready", render);
  new MutationObserver(render).observe(document.documentElement, {childList:true, subtree:true});
  render();
}());
