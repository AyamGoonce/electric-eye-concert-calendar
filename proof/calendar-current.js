(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3cdaaae76744bba9.js","sha256":"3cdaaae76744bba9a59909d1e2abaff070209c977119de993fc5e8e7a25317dd","count":2104,"publishedAt":"2026-11-15T16:25:06Z","state":"calendar-state.json","stateSha256":"93c46eeb7cc9810e9c5b659d6b6d652ad7e7db9ecdd7a0a5898d2e636e059c6e","sourceState":"calendar-source-state.json","sourceStateSha256":"1a85f6e74bfac4e63333ab391da2e0e0af97120da78742ecedc1a5b1de15fac7"});
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
