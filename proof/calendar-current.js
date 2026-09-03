(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cf0d911772e25375.js","sha256":"cf0d911772e253759b4e3b57b5da43c1d9f6d6a6e907d81a31d59e89b3cb2407","count":2516,"publishedAt":"2026-09-03T13:49:19Z","state":"calendar-state.json","stateSha256":"a1c84b6e7ac6a39da2bc5dfaa0f00b3ae84feaf39026bb3c5bedf7322d0b2a01"});
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
