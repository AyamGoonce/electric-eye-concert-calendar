(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2ac3231e155f0be7.js","sha256":"2ac3231e155f0be79ca4b27b19ea030133f1bbc6321f1dcc2a31211299a0f158","count":2045,"publishedAt":"2026-10-25T20:57:59Z","state":"calendar-state.json","stateSha256":"05d13420de6239426e5b595e9f4502e20cea92715ba7e61d9f02e1c867db35fc","sourceState":"calendar-source-state.json","sourceStateSha256":"1b34426dd865c924fcdab7f13fc0131b13f2bae04874ec284109964d201588da"});
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
