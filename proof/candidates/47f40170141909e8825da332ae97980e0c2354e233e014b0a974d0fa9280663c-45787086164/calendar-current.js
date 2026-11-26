(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.47f40170141909e8.js","sha256":"47f40170141909e8825da332ae97980e0c2354e233e014b0a974d0fa9280663c","count":2107,"publishedAt":"2026-11-26T08:54:34Z","state":"calendar-state.json","stateSha256":"6067d0d3505c4024ab4a16a661a22e117372259649d74476e67bda6e61488545","sourceState":"calendar-source-state.json","sourceStateSha256":"81c187b108bb82c61cb21634aed178a5baad399f28a9329f5fa53c7209a89880"});
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
