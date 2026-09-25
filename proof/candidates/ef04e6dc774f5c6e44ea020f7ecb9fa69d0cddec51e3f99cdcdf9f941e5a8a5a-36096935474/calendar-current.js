(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ef04e6dc774f5c6e.js","sha256":"ef04e6dc774f5c6e44ea020f7ecb9fa69d0cddec51e3f99cdcdf9f941e5a8a5a","count":2128,"publishedAt":"2026-09-25T05:03:34Z","state":"calendar-state.json","stateSha256":"ba9b900fe38ae7bf9d8072bc8e6fa14ed9a52b6d898d90633f2de23b2ecf587a","sourceState":"calendar-source-state.json","sourceStateSha256":"409acfd6d6f8c366b84c460dea2d98a26585d05dd7794e96d8474436d216b7e1"});
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
