(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.21a34dfdbd6d9561.js","sha256":"21a34dfdbd6d956134c5c197cbeaa5a78f00eae0f48b104d44bbe637bf602e46","count":2477,"publishedAt":"2026-09-11T16:36:56Z","state":"calendar-state.json","stateSha256":"25798227b4f12391c2f18480efd1aea2e23800a5cd56e2357e57f2c37b61fa17"});
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
