(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6477f4316063c623.js","sha256":"6477f4316063c623afdce8dae6f6c2d543fc922006e991ecfaa60516f0f43c4f","count":2064,"publishedAt":"2026-08-29T08:15:52Z","state":"calendar-state.json","stateSha256":"ef2df5b8c8049a7808ff05e570dc4e5ee7f47d63b8d8b7380d0d1aad58ddec93"});
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
