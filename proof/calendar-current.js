(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b3a9e884e38a310d.js","sha256":"b3a9e884e38a310d29b8b0ba5be197181e5032998ee1e004f2083e893f740c69","count":1745,"publishedAt":"2026-08-26T13:24:49Z","state":"calendar-state.json","stateSha256":"fe123557e9126c4ba288c8325a261a99d96d30dffb1b50a0ac18f2d2c75f9dc0"});
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
