(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.33016e9c3ec50079.js","sha256":"33016e9c3ec50079a7c8f0708617e46c482cfda10106a37bc0d8c8e0e55c28d3","count":2466,"publishedAt":"2026-09-06T13:21:07Z","state":"calendar-state.json","stateSha256":"d7293b749fe9f0b8b61579effde6b08c16183230992322ab4b58004826a58ffc"});
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
