(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fdf21bc285ce3761.js","sha256":"fdf21bc285ce37616d3bb7560a444871d62a98902231f7b3ad38d3f349b55a85","count":2152,"publishedAt":"2026-11-12T11:25:48Z","state":"calendar-state.json","stateSha256":"971e4ea5fe61b9856d67b116da0b00ae033e2109abdb0325c40d29e903b5f4a3","sourceState":"calendar-source-state.json","sourceStateSha256":"b5cf3a95cffb1b28b94a5c4bbbac5e4053dbac189be717164e33583d480e2e98"});
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
