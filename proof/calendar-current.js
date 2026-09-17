(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c9c71fb3e8772c64.js","sha256":"c9c71fb3e8772c640eb89bd597b56c089ccf3b249c360b49a564e80c10074573","count":2455,"publishedAt":"2026-09-17T21:30:52Z","state":"calendar-state.json","stateSha256":"5386093d8c7b00fa02fc52e1bda1b0be529329cfc4928eae3f2bf5d36c01b73c"});
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
