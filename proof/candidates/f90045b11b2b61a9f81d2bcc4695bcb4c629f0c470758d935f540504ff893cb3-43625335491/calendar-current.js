(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f90045b11b2b61a9.js","sha256":"f90045b11b2b61a9f81d2bcc4695bcb4c629f0c470758d935f540504ff893cb3","count":2137,"publishedAt":"2026-11-14T18:13:27Z","state":"calendar-state.json","stateSha256":"2b648cdd2d1a6bdc17bd6d52b939988c6edbb3afefc52b945a37b0e29f718505","sourceState":"calendar-source-state.json","sourceStateSha256":"1644fe1855331381ec09bfd8ef840d5f542a04ee449ac5c235fdfca126d7c7ff"});
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
