(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4af1759330604459.js","sha256":"4af17593306044595470534cbe13da29da899d14ef86b21da93a1e5888cfe69c","count":2266,"publishedAt":"2026-09-01T17:01:12Z","state":"calendar-state.json","stateSha256":"4579616219964482ae8cc659be87d7aa883185dff76bc59abd344498b572aa57"});
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
