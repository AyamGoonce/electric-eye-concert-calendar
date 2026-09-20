(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.878f515d5cb04102.js","sha256":"878f515d5cb041028806f6e1c0d1872d926341ad626f76bbfe9e688f9924ea4c","count":2175,"publishedAt":"2026-09-20T05:02:11Z","state":"calendar-state.json","stateSha256":"fdff45511d43c7f177f124fb5f41b897800487c2b29b94e0bca6d0f8d3b6b5b6"});
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
