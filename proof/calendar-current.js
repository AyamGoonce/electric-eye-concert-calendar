(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dd18d230e92c982c.js","sha256":"dd18d230e92c982c126bafc82d49a72848f5d90f1bfa29e1dd778f81a9cb1832","count":2056,"publishedAt":"2026-10-31T19:22:21Z","state":"calendar-state.json","stateSha256":"d2f86ba128e1660c3d07827c12cf75664c5754955960cf5116582ae2421d366e","sourceState":"calendar-source-state.json","sourceStateSha256":"341143261ff4b7147338b1f4da614e3816d537582e41809f32c2da61efa47ee3"});
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
