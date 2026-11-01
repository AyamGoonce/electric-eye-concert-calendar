(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3d0a719318c3b0b9.js","sha256":"3d0a719318c3b0b932ce52e38d60efebe89a34da6cdea70ec37c0c22030bf68c","count":2032,"publishedAt":"2026-11-01T00:13:21Z","state":"calendar-state.json","stateSha256":"7a30054ba0457a221abae72ce3ceaa2c57f7d00853b002909b5e7284d44acf9f","sourceState":"calendar-source-state.json","sourceStateSha256":"943f827379ee8c5ba7b69c04f9a37bd4a8333addda365d10290eac14fb4f8b78"});
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
