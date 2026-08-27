(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1dd1365c2f1ba022.js","sha256":"1dd1365c2f1ba02232091330df7a69634510f1aba0ae8e9d118d5eee6dc32ec9","count":1851,"publishedAt":"2026-08-27T21:44:40Z","state":"calendar-state.json","stateSha256":"44cdb2be9761e38ca83e4a3c116a90cb5853e10c429a7c49fc3df93fc53eb09e"});
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
