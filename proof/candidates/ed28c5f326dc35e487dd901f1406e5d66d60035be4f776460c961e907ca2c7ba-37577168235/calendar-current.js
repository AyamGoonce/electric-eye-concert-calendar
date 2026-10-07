(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ed28c5f326dc35e4.js","sha256":"ed28c5f326dc35e487dd901f1406e5d66d60035be4f776460c961e907ca2c7ba","count":2195,"publishedAt":"2026-10-07T05:47:12Z","state":"calendar-state.json","stateSha256":"840bcd44245cfab3e6f0613e7f31cc8687a008368f89317b9d9ad5c206c7d05e","sourceState":"calendar-source-state.json","sourceStateSha256":"6a3d32736a04f9909cc047ebd786847ab8639d6113800cae44959bb4442c3c57"});
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
