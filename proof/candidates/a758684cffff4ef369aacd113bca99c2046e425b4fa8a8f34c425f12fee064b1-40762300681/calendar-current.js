(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a758684cffff4ef3.js","sha256":"a758684cffff4ef369aacd113bca99c2046e425b4fa8a8f34c425f12fee064b1","count":2066,"publishedAt":"2026-10-28T20:21:41Z","state":"calendar-state.json","stateSha256":"0d8d2a921e6e6aec13c0969e2b26fb747ea0903f834f2e18b7b0ea9924f64dbe","sourceState":"calendar-source-state.json","sourceStateSha256":"84b6b160d82d3e078c9fd26310fec2c984f949b9791a4e9f973919918d5e00f9"});
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
