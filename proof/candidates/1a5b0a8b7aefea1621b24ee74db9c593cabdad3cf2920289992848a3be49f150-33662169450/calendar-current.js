(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1a5b0a8b7aefea16.js","sha256":"1a5b0a8b7aefea1621b24ee74db9c593cabdad3cf2920289992848a3be49f150","count":2251,"publishedAt":"2026-09-02T17:45:45Z","state":"calendar-state.json","stateSha256":"c2e911c31bf461d7871c4a2871f1ed53c0fc169aec541193642f9fd7bd057962"});
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
