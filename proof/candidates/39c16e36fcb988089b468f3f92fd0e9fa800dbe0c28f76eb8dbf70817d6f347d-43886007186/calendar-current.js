(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.39c16e36fcb98808.js","sha256":"39c16e36fcb988089b468f3f92fd0e9fa800dbe0c28f76eb8dbf70817d6f347d","count":2105,"publishedAt":"2026-11-16T14:30:14Z","state":"calendar-state.json","stateSha256":"3c60dc40ea2e00c3a12c235ba0bd03cd51512e4e1bf2f9dd29037428b8e537fe","sourceState":"calendar-source-state.json","sourceStateSha256":"9ff87a088da34cda2e9e6b44bcd4ff03c8a1d996c8b3f92cb37e715e4673925f"});
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
