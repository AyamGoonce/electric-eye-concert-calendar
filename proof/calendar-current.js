(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e1e0742f02d8202c.js","sha256":"e1e0742f02d8202c6f873e6764300ec346a0b7f14382531a3db126ef8635459f","count":2104,"publishedAt":"2026-11-18T00:01:00Z","state":"calendar-state.json","stateSha256":"6d31b940e04b05c1fac43ad00b8bb6d17a2eaba0512242718ab58b17c5494d34","sourceState":"calendar-source-state.json","sourceStateSha256":"ee76f473274d4d42492c96b740e8e2d1e3489dfd9d5e128f1e86475ae21e8256"});
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
