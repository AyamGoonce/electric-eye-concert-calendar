(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.896d2e5f03856033.js","sha256":"896d2e5f038560337933de7a9c37094d10c82b7ab0d1cd3351f0b480f284b68f","count":2473,"publishedAt":"2026-09-03T23:27:40Z","state":"calendar-state.json","stateSha256":"263af834c2525db6bb657f72640ec81daf332eaab92a8c6714ae83c6e61eb1d4"});
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
