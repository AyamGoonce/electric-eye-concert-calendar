(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cede56b8320c7810.js","sha256":"cede56b8320c78107f63115a9eb3ff7022683471a47f487cf146b14ad335ece6","count":2467,"publishedAt":"2026-09-14T16:52:08Z","state":"calendar-state.json","stateSha256":"77ec39605c8b0bc756588da5a161c6787854f442b63e6be3b11e8e3e84b3d7d4"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
