(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4d1e652cdf619d82.js","sha256":"4d1e652cdf619d8271b98e1e8cf64e8233521371b51aad5c82be93e79ae84cf9","count":2124,"publishedAt":"2026-09-25T15:11:35Z","state":"calendar-state.json","stateSha256":"c9af02d2a8f68574c97c26d90535ff3fcfd9e06b6df37be26513c78469777e82","sourceState":"calendar-source-state.json","sourceStateSha256":"f662f56fe1529bfb3d413dca18c84f39de8ef80914cff2c06e8b603bec19fc21"});
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
