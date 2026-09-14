(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3cca095e9e7bd9a0.js","sha256":"3cca095e9e7bd9a03653a00f8c6a4f98d3371b6db221db8b1261d6b3fc23229e","count":2466,"publishedAt":"2026-09-14T19:56:06Z","state":"calendar-state.json","stateSha256":"eb1f42f66bcc71156650fed36f7709067b05e6abf4ebe9fae126e62ce2a9d825"});
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
