(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fe4433e187f81bc9.js","sha256":"fe4433e187f81bc9e9e393061ddbcf318f4426c0edaca9701ab8eeb11cf59850","count":2066,"publishedAt":"2026-08-28T22:29:43Z","state":"calendar-state.json","stateSha256":"e4ad1e59910a542b9e22fee7ee619af8a264eb491d891b12fb0a5dab8ee4c8bb"});
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
