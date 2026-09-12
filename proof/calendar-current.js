(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ba2568ba551dc7d6.js","sha256":"ba2568ba551dc7d64cbf4d1a287a2e9abecc588b4bd5abb56e26d35853732af9","count":2475,"publishedAt":"2026-09-12T20:46:50Z","state":"calendar-state.json","stateSha256":"03a19bdb7a0ba19d475e63034e6d4647d19a1bcdcddb5a19bc198209e44b786c"});
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
