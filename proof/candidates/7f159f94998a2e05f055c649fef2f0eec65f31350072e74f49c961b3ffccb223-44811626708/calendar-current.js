(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7f159f94998a2e05.js","sha256":"7f159f94998a2e05f055c649fef2f0eec65f31350072e74f49c961b3ffccb223","count":2147,"publishedAt":"2026-11-20T20:28:40Z","state":"calendar-state.json","stateSha256":"6fbf36149a075ab23eb405878f3255467c5c775762e993778b897fcc90397b41","sourceState":"calendar-source-state.json","sourceStateSha256":"81a482cd4b0c8a9c806f4b4deacd76611b3537170023a0110673e7b764306edf"});
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
