(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.343f7a5948ae8a82.js","sha256":"343f7a5948ae8a8216f90dbe7df43253e971e5887a1e83b693179b4a2e997cb4","count":2054,"publishedAt":"2026-08-31T05:48:13Z","state":"calendar-state.json","stateSha256":"8688ae5609e033e8d2a7c2e2d830f44eaf6ae0b50b6d59c936865eef7b26992e"});
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
