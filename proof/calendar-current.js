(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6afc27a29da4b68f.js","sha256":"6afc27a29da4b68f8c4aa51c09530935fd9d83682f7505ac71c46eaf96004ffc","count":2465,"publishedAt":"2026-09-06T23:40:23Z","state":"calendar-state.json","stateSha256":"a95442ab66e7950b0ceb4cdb9c56b35432b4df6f4c19230dd860040f5f48c6c3"});
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
