(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d2e99af881556ea6.js","sha256":"d2e99af881556ea6d98ec3556b070406c2a845444ba699a946c2901cfcf32489","count":2084,"publishedAt":"2026-10-30T22:28:46Z","state":"calendar-state.json","stateSha256":"bbaa2c45b4cc2a70c5fb33d6cd79ab7b4cada202a707d56afdfb4a464aed2f6a","sourceState":"calendar-source-state.json","sourceStateSha256":"21e94469e23836edbcc8f1fc96e46c19dadefe7b44c1fcbfdcfadcc8d2d6ab17"});
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
