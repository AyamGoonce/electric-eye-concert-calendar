(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d8c337a8f6801117.js","sha256":"d8c337a8f68011178384d4000d8bbd7f349c0fe8b100e0ea4dc836092bc80ab7","count":2487,"publishedAt":"2026-09-09T09:36:38Z","state":"calendar-state.json","stateSha256":"20de49af1f5e44449ba398dc8ab74cd9cd164d80fc6bb06eb408568cd5030f64"});
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
