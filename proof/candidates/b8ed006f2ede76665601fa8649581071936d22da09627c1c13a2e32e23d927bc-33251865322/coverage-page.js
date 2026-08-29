(function () {
  "use strict";
  var calendarUrl = "https://www.electriceyerock.com/p/paris-area-concert-calendar.html";
  var headings = {concert_review:"Concert Reviews",interview:"Interviews",album_review:"Album Reviews",news:"News",playlist:"Playlists",other:"More from Electric Eye"};
  function text(parent, tag, value, cls) { var node=document.createElement(tag);node.textContent=value;if(cls)node.className=cls;parent.append(node);return node; }
  function humanDate(value) { return new Intl.DateTimeFormat("en-GB",{day:"numeric",month:"long",year:"numeric",timeZone:"UTC"}).format(new Date(value+"T12:00:00Z")); }
  function render() {
    var mount=document.getElementById("ee-coverage-results"),index=window.ElectricEyeContentIndex,data=window.ElectricEyeConcertData;
    if(!mount||!index||!data||mount.dataset.ready)return;
    var id=new URLSearchParams(location.search).get("event")||"",event=data.find(function(item){return item.i===id;});
    if(!event){text(mount,"p","No matching concert coverage was found.","ee-artist-empty");return;}
    mount.dataset.ready="1";text(mount,"p","Electric Eye","ee-page-kicker");text(mount,"h1",event.h,"ee-artist-title");
    text(mount,"p",humanDate(event.d)+" · "+event.v+(event.c.toLowerCase()==="paris"?"":" · "+event.c),"ee-page-context");
    var actions=document.createElement("div");actions.className="ee-page-actions";
    var back=document.createElement("a");back.href=calendarUrl+"#event-"+event.i;back.textContent="View in Concert Calendar";actions.append(back);
    if(event.t){var tickets=document.createElement("a");tickets.href=event.t;tickets.target="_blank";tickets.rel="noopener noreferrer";tickets.textContent="Tickets";actions.append(tickets);}
    var officialSeen=new Set();(event.ee||[]).forEach(function(item){var artist=index.artists[item.slug];if(!artist||!artist.os||officialSeen.has(artist.os))return;officialSeen.add(artist.os);var official=document.createElement("a");official.href=artist.os;official.target="_blank";official.rel="noopener noreferrer";official.textContent=artist.n+" Official Site";actions.append(official);});mount.append(actions);
    text(mount,"h2","Electric Eye Coverage","ee-coverage-heading");
    var slugs=(event.ee||[]).map(function(link){return link.slug;}),articles=new Map();
    slugs.forEach(function(slug){var artist=index.artists[slug];if(!artist)return;artist.ar.forEach(function(articleId){var article=index.articles[articleId],record=articles.get(article.u);if(!record){record={article:article,artists:[]};articles.set(article.u,record);}if(!record.artists.includes(artist.n))record.artists.push(artist.n);});});
    Object.keys(headings).forEach(function(kind){var records=Array.from(articles.values()).filter(function(record){return record.article.y===kind;}).sort(function(a,b){return b.article.d.localeCompare(a.article.d);});if(!records.length)return;
      var section=document.createElement("section");text(section,"h2",headings[kind]);var list=document.createElement("ul");
      records.forEach(function(record){var item=document.createElement("li");item.className="ee-article-card";if(record.article.im){var image=document.createElement("img");image.src=record.article.im;image.alt="";image.loading="lazy";image.decoding="async";image.width=96;image.height=72;item.append(image);}var copy=document.createElement("div");var link=document.createElement("a");link.href=record.article.u;link.textContent=record.article.t;copy.append(link);var meta=text(copy,"p",humanDate(record.article.d),"ee-article-meta");if(record.artists.length>1)meta.append(document.createTextNode(" · Related artists: "+record.artists.join(", ")));item.append(copy);list.append(item);});section.append(list);mount.append(section);
    });
  }
  document.addEventListener("ee:content-index-ready",render);document.addEventListener("ee:concert-data-ready",render);document.addEventListener("DOMContentLoaded",render);render();
}());
