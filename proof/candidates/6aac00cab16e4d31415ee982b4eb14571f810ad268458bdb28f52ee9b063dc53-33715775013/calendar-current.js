(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6aac00cab16e4d31.js","sha256":"6aac00cab16e4d31415ee982b4eb14571f810ad268458bdb28f52ee9b063dc53","count":2267,"publishedAt":"2026-09-03T04:47:37Z","state":"calendar-state.json","stateSha256":"d0b620d9cfa7a8de8bf9b9c83fedb5e965daa3dfa04f48d944c8fbdad4ac2a68"});
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
