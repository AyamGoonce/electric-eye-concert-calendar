(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.39da0296b56c8787.js","sha256":"39da0296b56c878790ed9015362485e2d57ad731b0e6116b3c7cc989244f6d77","count":2054,"publishedAt":"2026-08-29T00:20:12Z","state":"calendar-state.json","stateSha256":"62479807a889a413ccd432fb624161289e8f7d3c07b27d12cc7025499a8c163d"});
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
