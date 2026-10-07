(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b7060c04fe62f3b9.js","sha256":"b7060c04fe62f3b9c64d7794e7aaaaaf91774c25ba03baaf14b60fa981ce4e87","count":2220,"publishedAt":"2026-10-07T16:39:27Z","state":"calendar-state.json","stateSha256":"ec9fa0a8cbe6dede7d34b0009497900154a097c54b5329a9a812bc91e8bab4ad","sourceState":"calendar-source-state.json","sourceStateSha256":"e7f63fd0ecf3cbb0f8299b349a38bce001beaea263da062cb0916fe1fe3f4d4b"});
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
