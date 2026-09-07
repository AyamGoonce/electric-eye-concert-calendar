(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ae99a236da93bb49.js","sha256":"ae99a236da93bb49d8052bc86a809f954fcd79680d2be4c5e58b8b0d22275f24","count":2390,"publishedAt":"2026-09-07T04:59:19Z","state":"calendar-state.json","stateSha256":"1ccbdd4ec96aea6b73ac650d6dde4b76ecd0cf7dedec9ae1e634f815379a3e61"});
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
