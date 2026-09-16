(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7a25064488419502.js","sha256":"7a2506448841950270e35f379f1eda02636d8d643ed53e66558fd7dab3ab0621","count":2474,"publishedAt":"2026-09-16T21:27:32Z","state":"calendar-state.json","stateSha256":"24079f948eebedd0c927a23e2b62f2680431e5fee889227e0b9eddd01b283048"});
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
