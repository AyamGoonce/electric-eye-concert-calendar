(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7f6c49d25fcc3a27.js","sha256":"7f6c49d25fcc3a27005a0da14b03197668ac842a315d808a93f4f2520d657fd9","count":1708,"publishedAt":"2026-08-23T13:08:19Z","state":"calendar-state.json","stateSha256":"d9cbd395c3d90f62288b3d95f812c35537a987da184f5f990fd7ce264a5a2475"});
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
