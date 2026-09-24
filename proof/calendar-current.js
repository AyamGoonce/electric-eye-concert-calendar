(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.78be4cf77867ae03.js","sha256":"78be4cf77867ae03498c2f41a2a1a9b57bb106cc178cc619db076161c552fd78","count":2136,"publishedAt":"2026-09-24T11:54:16Z","state":"calendar-state.json","stateSha256":"967ecb43fe57c5d437a01809c0221f1218be3887e932fa398c9ce2266888550e","sourceState":"calendar-source-state.json","sourceStateSha256":"c7446c25d051935b0794f453478301dcc9498772b81a8805a6cdbf4864fbcc2e"});
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
