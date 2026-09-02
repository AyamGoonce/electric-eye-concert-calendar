(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6b8c1dc2d267bba2.js","sha256":"6b8c1dc2d267bba2a470505c0ae2024a77098779b6efeef3bf0a33aa8c767505","count":2247,"publishedAt":"2026-09-02T11:30:30Z","state":"calendar-state.json","stateSha256":"3a85dbc9458b44d7aa6fb497895a81d653e1d00401f325a503a07cd756de6c14"});
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
