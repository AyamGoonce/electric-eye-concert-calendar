(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e5dcf66166b458aa.js","sha256":"e5dcf66166b458aa79f9fa51ac05ae98dc2260a4be977328fdd00ffb6e26defb","count":2223,"publishedAt":"2026-10-02T18:59:42Z","state":"calendar-state.json","stateSha256":"2f31c22a3f08ed00a5a81a3a9ca92f83c9bb0a5c819344b324dd93d96b73afea","sourceState":"calendar-source-state.json","sourceStateSha256":"3f1d1680e1bc40327d483f8f83a3221af1fc2bbef08114200c55f21910521198"});
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
