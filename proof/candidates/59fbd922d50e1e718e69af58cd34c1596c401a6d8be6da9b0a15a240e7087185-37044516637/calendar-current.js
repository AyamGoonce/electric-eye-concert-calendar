(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.59fbd922d50e1e71.js","sha256":"59fbd922d50e1e718e69af58cd34c1596c401a6d8be6da9b0a15a240e7087185","count":2224,"publishedAt":"2026-10-02T18:01:08Z","state":"calendar-state.json","stateSha256":"c1ce0ab9739ee4c0fe16dc2e765917e0426170fd0c3d7362f1bbef02c6cd58a0","sourceState":"calendar-source-state.json","sourceStateSha256":"dc11bcf45ae089b91679c8be9d40815146efc213009c5a64604832daea249491"});
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
