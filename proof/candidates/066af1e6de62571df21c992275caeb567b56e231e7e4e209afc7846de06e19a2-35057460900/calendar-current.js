(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.066af1e6de62571d.js","sha256":"066af1e6de62571df21c992275caeb567b56e231e7e4e209afc7846de06e19a2","count":2434,"publishedAt":"2026-09-16T05:00:13Z","state":"calendar-state.json","stateSha256":"0b649d62a838447f278554d0e1ac7846069527ef087008bf605f952c7f2abba2"});
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
