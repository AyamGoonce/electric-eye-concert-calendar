(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9577089df9b40954.js","sha256":"9577089df9b409548755428dd5107b55945c5f9a27c83e197ca961ad69c503e4","count":2194,"publishedAt":"2026-10-10T00:59:10Z","state":"calendar-state.json","stateSha256":"307890e0ea31ee26d76e15dec71aaf391fc928d5fa7ba55715ccb7961073f58f","sourceState":"calendar-source-state.json","sourceStateSha256":"c3565b3747d67a7a952cc1f2ad83f5e57bfc8726632d90d524ba893b06e36d3d"});
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
