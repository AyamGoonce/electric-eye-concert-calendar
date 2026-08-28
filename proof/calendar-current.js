(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.815890d2b71bda1e.js","sha256":"815890d2b71bda1e73605e47bb4ff10e8e9764b1ab39a568376c26690fbb062a","count":1848,"publishedAt":"2026-08-28T08:31:53Z","state":"calendar-state.json","stateSha256":"bcbd438b33ed9af43e5dd30b785dcc6a69b19dc618dc579660e3655435b5f455"});
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
