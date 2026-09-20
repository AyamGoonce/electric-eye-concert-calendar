(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8a7ce61ba0e93c32.js","sha256":"8a7ce61ba0e93c3241ab5bb6ef47e19f40eee829fa10db0ecee69d9df0046d7d","count":2172,"publishedAt":"2026-09-20T09:16:18Z","state":"calendar-state.json","stateSha256":"1bd1dad4039d143ead949cbe33471d18d4337b63e6245cfa23482173b37a6595"});
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
