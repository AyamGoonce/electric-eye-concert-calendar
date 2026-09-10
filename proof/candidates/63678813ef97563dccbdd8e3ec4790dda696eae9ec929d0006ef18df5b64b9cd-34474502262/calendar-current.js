(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.63678813ef97563d.js","sha256":"63678813ef97563dccbdd8e3ec4790dda696eae9ec929d0006ef18df5b64b9cd","count":2500,"publishedAt":"2026-09-10T12:04:41Z","state":"calendar-state.json","stateSha256":"654c0149290384a888db413361725a3255d44dc330d0226d03cf9fd88ec8f5de"});
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
