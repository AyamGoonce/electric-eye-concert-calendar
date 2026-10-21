(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b076183a45898266.js","sha256":"b076183a4589826606daef35ed7d75c3e74cfcf47df309f5fc4bac1669cb5e72","count":2068,"publishedAt":"2026-10-21T10:31:35Z","state":"calendar-state.json","stateSha256":"89fc3f4609c934a6725bb70a4043f6deac2d78001e24e50760c85076832dc3b5","sourceState":"calendar-source-state.json","sourceStateSha256":"cdfb6a71c5086ba687a3fe5a87d2f12e91642ed9c8bf2d8946652e551ed77846"});
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
