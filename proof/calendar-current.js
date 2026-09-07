(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2977faf5f57d3428.js","sha256":"2977faf5f57d3428371e1aab499e1e4d9fd79272c08d938af985a2f66fa83ae3","count":2479,"publishedAt":"2026-09-07T18:18:21Z","state":"calendar-state.json","stateSha256":"cebedde9e58e32ccf68d58ac74b5a2ad18735f919d77174f05b4896a1cffda44"});
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
