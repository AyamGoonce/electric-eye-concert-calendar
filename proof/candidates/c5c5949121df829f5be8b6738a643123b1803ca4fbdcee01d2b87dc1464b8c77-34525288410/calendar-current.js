(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c5c5949121df829f.js","sha256":"c5c5949121df829f5be8b6738a643123b1803ca4fbdcee01d2b87dc1464b8c77","count":2487,"publishedAt":"2026-09-10T20:18:51Z","state":"calendar-state.json","stateSha256":"e9e5ef0dc733755120163091c0780969041da749a75c3b205797d44bd488400e"});
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
