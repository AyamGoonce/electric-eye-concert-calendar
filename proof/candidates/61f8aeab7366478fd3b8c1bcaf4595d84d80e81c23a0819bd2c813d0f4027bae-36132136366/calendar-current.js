(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.61f8aeab7366478f.js","sha256":"61f8aeab7366478fd3b8c1bcaf4595d84d80e81c23a0819bd2c813d0f4027bae","count":2136,"publishedAt":"2026-09-25T11:56:57Z","state":"calendar-state.json","stateSha256":"4b7d58ad28b30c27a6c2072c76fa6c9fd66174af5f61caa89d0816965985923b","sourceState":"calendar-source-state.json","sourceStateSha256":"ccbc5847e3f67414ad4ae9fd918efe3d67a19da02f94c9e4a56474a188f3ef9b"});
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
