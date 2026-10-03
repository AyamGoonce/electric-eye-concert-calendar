(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.983e5c50c675ec28.js","sha256":"983e5c50c675ec2863fef31a3005281e7d498a7e716aa6d1298e2eb7a2646e62","count":2201,"publishedAt":"2026-10-03T05:24:36Z","state":"calendar-state.json","stateSha256":"8500c9aac44c749e44862340f9d486039eeb3dfa03f0f9c567de9fa48ed8b1bf","sourceState":"calendar-source-state.json","sourceStateSha256":"000d0bae41f20e46a6ccb3eab9efa8b62c08a02c654b045335987178d5c93030"});
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
