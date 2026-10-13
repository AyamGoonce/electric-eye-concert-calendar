(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9eb6e4dc722ecf14.js","sha256":"9eb6e4dc722ecf143125a0a6c834d46df7b8ff7449d05ea23989a5da0b51a73c","count":2162,"publishedAt":"2026-10-13T17:01:22Z","state":"calendar-state.json","stateSha256":"89daef3e104bd00c93255f473d7a69595160757de720447900199dc0626c9d2e","sourceState":"calendar-source-state.json","sourceStateSha256":"a2ffa6f956110839c64e3d9fc71e9e0238acb3c3c2fbd89f6948eff35fa3f3a3"});
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
