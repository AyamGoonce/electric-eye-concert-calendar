(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6feeca583374e837.js","sha256":"6feeca583374e8374a6e4e4a908c22d49358abedd96d62dac9e8166d8523feaf","count":2224,"publishedAt":"2026-10-01T10:20:38Z","state":"calendar-state.json","stateSha256":"9401394fbf07a8be79a3d3671252b4d983cc30f4e146a58babe23a885a2a395b","sourceState":"calendar-source-state.json","sourceStateSha256":"e308a60f143e9b90b34d9e1e6395a0edfedb74b43824b2013a798aab64eae856"});
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
