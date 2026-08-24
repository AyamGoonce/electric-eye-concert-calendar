(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.385a4b11dac7f7e0.js","sha256":"385a4b11dac7f7e0caf2774ff4830f9a267a9929183ee6bd6e72fea4d4326dd4","count":1732,"publishedAt":"2026-08-24T18:18:36Z","state":"calendar-state.json","stateSha256":"1265375f145ca698ab204b33f9df9d993ba3345fbc89dfe226af0fa0630c5e2f"});
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
