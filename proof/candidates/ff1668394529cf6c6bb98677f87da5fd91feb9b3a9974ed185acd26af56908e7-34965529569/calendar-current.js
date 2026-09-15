(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ff1668394529cf6c.js","sha256":"ff1668394529cf6c6bb98677f87da5fd91feb9b3a9974ed185acd26af56908e7","count":2480,"publishedAt":"2026-09-15T11:55:27Z","state":"calendar-state.json","stateSha256":"a1d0617d765240aac76053c13bf330e5d76cfc0cd0f95faa87d7c1bd7dfddaea"});
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
