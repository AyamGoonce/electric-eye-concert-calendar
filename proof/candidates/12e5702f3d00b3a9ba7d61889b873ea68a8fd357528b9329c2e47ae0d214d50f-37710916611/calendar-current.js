(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.12e5702f3d00b3a9.js","sha256":"12e5702f3d00b3a9ba7d61889b873ea68a8fd357528b9329c2e47ae0d214d50f","count":2206,"publishedAt":"2026-10-08T01:05:02Z","state":"calendar-state.json","stateSha256":"01971a47eefce8ec40ed5c043b8c5fc6d7709dfe580fe707b628aa53f4d18a53","sourceState":"calendar-source-state.json","sourceStateSha256":"53f762f3bd6f8a86db37f90a539c5e8b7bfe2efbdc0cc1ce23656432c744f560"});
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
