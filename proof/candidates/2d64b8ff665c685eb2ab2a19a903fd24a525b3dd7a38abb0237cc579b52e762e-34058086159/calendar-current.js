(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2d64b8ff665c685e.js","sha256":"2d64b8ff665c685eb2ab2a19a903fd24a525b3dd7a38abb0237cc579b52e762e","count":2400,"publishedAt":"2026-09-06T20:38:21Z","state":"calendar-state.json","stateSha256":"076e4c82be1159943e2503c39a707ec024618846e7c840096e3ae2ae740cbc12"});
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
