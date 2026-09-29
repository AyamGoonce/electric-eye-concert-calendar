(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.abcac73517ef2974.js","sha256":"abcac73517ef2974e389def6a63039485023e27a93feac63d3506229e2740bcd","count":2138,"publishedAt":"2026-09-29T22:21:06Z","state":"calendar-state.json","stateSha256":"b7047f71b2c733059c5f9c1f12a7052150d9d768b7379f6ebbe560c7b52d713a","sourceState":"calendar-source-state.json","sourceStateSha256":"b95ba9da8b1b1cc9cdbfaaadcb9f100e6261e577eacdc0990ca46980c740d51b"});
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
