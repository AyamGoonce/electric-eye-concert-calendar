(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b0d91fb17adef03e.js","sha256":"b0d91fb17adef03eed575e648f07a7ea85ae09f726c923ab244f8804b55c048c","count":2524,"publishedAt":"2026-09-03T12:50:16Z","state":"calendar-state.json","stateSha256":"5de20a4083ac1deab2b0976cfedfbb072d69353ea6d3b369954afb87a9e5fb42"});
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
