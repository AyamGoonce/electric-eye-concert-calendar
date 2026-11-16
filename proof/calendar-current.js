(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1d7151ead111e63a.js","sha256":"1d7151ead111e63a9526c6b43b9f69a260dcd2f0ddbea1105d86ceddf82c4063","count":2085,"publishedAt":"2026-11-16T00:44:15Z","state":"calendar-state.json","stateSha256":"65914897a2ff8109b6b2a8341cad4c9d39c1baf3b27cd7479d228fc3e960ed37","sourceState":"calendar-source-state.json","sourceStateSha256":"ee79a947f3ef42d3635e9be3da553ac1a651a8d82d6eb6a956728ab3683f0254"});
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
