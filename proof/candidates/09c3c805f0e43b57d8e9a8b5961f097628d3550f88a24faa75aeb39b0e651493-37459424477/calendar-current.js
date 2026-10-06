(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.09c3c805f0e43b57.js","sha256":"09c3c805f0e43b57d8e9a8b5961f097628d3550f88a24faa75aeb39b0e651493","count":2200,"publishedAt":"2026-10-06T11:56:09Z","state":"calendar-state.json","stateSha256":"b3e3cf6bf96c4c51dd802f76a1050ef27b4eebcad21b68ebdb23af63406de061","sourceState":"calendar-source-state.json","sourceStateSha256":"4d1fc1df77c72ebc899dec4a0a38cdbacd11a1061afa7946ac30200292ed8eb9"});
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
