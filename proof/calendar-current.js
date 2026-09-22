(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.84bb9c4e9f0fa712.js","sha256":"84bb9c4e9f0fa7127bfbeb8d3b6be9d85ab2d5d2b9e8df04450e010c15ae48a1","count":2103,"publishedAt":"2026-09-22T00:13:34Z","state":"calendar-state.json","stateSha256":"c882db681914f6de96a18fbb7413461642f8112367803c9b7aeddfd5cab5bcbc"});
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
