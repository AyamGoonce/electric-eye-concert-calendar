(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f94c738ed16a37b9.js","sha256":"f94c738ed16a37b9d125e0a6e6c69762916c4e988979807b19c2ac04b188c863","count":1820,"publishedAt":"2026-08-28T09:17:24Z","state":"calendar-state.json","stateSha256":"11e186ad4ef38022266e7f775dade799887ebd403d2cdd35064e559fb53e2be1"});
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
