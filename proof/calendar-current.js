(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.962cfbcec46f75c7.js","sha256":"962cfbcec46f75c79556d685d6bcf1375e7f3eed4d2051fbca470accd1a528a6","count":2521,"publishedAt":"2026-09-09T21:02:13Z","state":"calendar-state.json","stateSha256":"80d9312cb8c1acb2795389595b2e050a30b8db9cf73929694f1ed00b688cf1fa"});
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
