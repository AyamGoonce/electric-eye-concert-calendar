(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.325f2d3c68a5f483.js","sha256":"325f2d3c68a5f483bb152e8cc5a613d72f7ae306ff1445449e4edffd50fb763b","count":2136,"publishedAt":"2026-10-16T15:52:33Z","state":"calendar-state.json","stateSha256":"46b8ed52e232313a75c9905aa65c5c44bde50fafa23a29a4ef8a14692cc34cc6","sourceState":"calendar-source-state.json","sourceStateSha256":"54a936802b2d35a8ac6e0cdc21ed2f30cdf9944d2af5306e49d2e25881443ee1"});
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
