(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4b5be8a9c7bed927.js","sha256":"4b5be8a9c7bed927f19fbefcbc9699769d8d3705b7462b5b8e0e16dc91323b7b","count":2122,"publishedAt":"2026-09-22T05:11:23Z","state":"calendar-state.json","stateSha256":"a4a00838456ce7ec233e8c24717657c6dfb63bd4c7166ebf125e5ca6ceb30064"});
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
