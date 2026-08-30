(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e491bbf6aa5e00d2.js","sha256":"e491bbf6aa5e00d2683277c9369de9d3c75a6e2318e67f696a354109cbd90335","count":2057,"publishedAt":"2026-08-30T21:17:24Z","state":"calendar-state.json","stateSha256":"04d61c3db9463a88291d3ee5a75b00dbeb25fc6ed56a598a5c15cb479c1d9773"});
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
