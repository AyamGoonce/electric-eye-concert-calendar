(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f629b4e79256aef5.js","sha256":"f629b4e79256aef59d1bffa57ee3a7c3a01774127748b7025b8f111f863900c9","count":2194,"publishedAt":"2026-10-10T09:58:28Z","state":"calendar-state.json","stateSha256":"696b02bb355f768c58d67b53ed9351219e8c741b62e2d5e95338a731b3b179f5","sourceState":"calendar-source-state.json","sourceStateSha256":"cc596f9ee8afa86f50344123fcf5f70434d0546d33f813b540deadad209dfb6a"});
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
