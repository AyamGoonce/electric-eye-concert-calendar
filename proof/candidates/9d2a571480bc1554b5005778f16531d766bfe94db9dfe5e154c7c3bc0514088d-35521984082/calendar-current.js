(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9d2a571480bc1554.js","sha256":"9d2a571480bc1554b5005778f16531d766bfe94db9dfe5e154c7c3bc0514088d","count":2175,"publishedAt":"2026-09-20T16:16:45Z","state":"calendar-state.json","stateSha256":"923725b813636938b06109ca340d3dfccbe3787899a7f08c066fbe4c9d86520c"});
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
