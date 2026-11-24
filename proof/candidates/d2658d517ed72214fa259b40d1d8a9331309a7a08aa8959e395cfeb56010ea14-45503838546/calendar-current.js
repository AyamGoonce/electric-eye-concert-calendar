(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d2658d517ed72214.js","sha256":"d2658d517ed72214fa259b40d1d8a9331309a7a08aa8959e395cfeb56010ea14","count":2116,"publishedAt":"2026-11-24T22:45:41Z","state":"calendar-state.json","stateSha256":"2e347cfc3c5b688600e976daa9de82b0e5026c4dbc2c41217a9049d23cb0b63d","sourceState":"calendar-source-state.json","sourceStateSha256":"f0153782658e930bf9165b2d08ab64a7c5bac1e2d2f4bf6577116e5a0181c5af"});
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
