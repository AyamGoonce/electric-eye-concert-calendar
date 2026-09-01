(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cc883854889a7694.js","sha256":"cc883854889a7694e1b989d6c0f772efe4ccd09684f2a82b0854b4c6dde1b4e7","count":2266,"publishedAt":"2026-09-01T16:14:07Z","state":"calendar-state.json","stateSha256":"8dfb067b918e14db49e29aa58a78630e68ada1655dc623d2eb29b7f2d05f2c78"});
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
