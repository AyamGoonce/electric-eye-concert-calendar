(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bf2916430aa01c34.js","sha256":"bf2916430aa01c345029af043a00d4ad5dc6f48986ab158328b32a5868dd9999","count":1709,"publishedAt":"2026-08-23T12:43:41Z","state":"calendar-state.json","stateSha256":"0bf45a542361fa98180f7c2385ca6c38ac914c8bfb13913275ae373ae8c16483"});
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
