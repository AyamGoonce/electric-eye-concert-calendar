(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.68d8f9d6f36555e3.js","sha256":"68d8f9d6f36555e3330ce5a18e575552b86e87b92004b73eb0291bda1ccf601e","count":2221,"publishedAt":"2026-10-02T20:04:53Z","state":"calendar-state.json","stateSha256":"bfd2a04d84e56ccb695497507cbedb362fe7eb3d00de58de75707a9ec67bbeb7","sourceState":"calendar-source-state.json","sourceStateSha256":"a7468f9c590273f7cbd6c2ac3b98675e8a9021e2f26c82232e1350aed864deea"});
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
