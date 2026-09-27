(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c9501658fe8d5137.js","sha256":"c9501658fe8d5137b91230fed73599f6011d773089ff5b880d1e6b620f9b4182","count":2070,"publishedAt":"2026-09-27T12:09:29Z","state":"calendar-state.json","stateSha256":"4ce4982489da42e3a87eb5ef1fee65b3e79cc31d2b1d9b26595db65c1db2b384","sourceState":"calendar-source-state.json","sourceStateSha256":"cb74251c893be9f162aca89dbf9be3891652d88f71d57d5940fc1cbab3f236a8"});
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
