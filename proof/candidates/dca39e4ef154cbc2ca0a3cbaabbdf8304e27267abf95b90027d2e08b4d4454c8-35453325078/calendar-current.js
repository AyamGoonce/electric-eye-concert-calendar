(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dca39e4ef154cbc2.js","sha256":"dca39e4ef154cbc2ca0a3cbaabbdf8304e27267abf95b90027d2e08b4d4454c8","count":2198,"publishedAt":"2026-09-19T15:59:25Z","state":"calendar-state.json","stateSha256":"8f5246108d1f44f2420a5bf5a4ae505c7e8cb81b1f39c683b6abddef7e8b5e6d"});
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
