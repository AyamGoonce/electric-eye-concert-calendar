(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b246fab67bd40d70.js","sha256":"b246fab67bd40d702794adc2d2fdd4f0e84e274852ce3dfbb9093b809d5bd4b6","count":2185,"publishedAt":"2026-11-11T11:04:45Z","state":"calendar-state.json","stateSha256":"03ef417f6b768a3074ad68ffbf4ce169340bef3a502cc14891e9ec9c2be1dc10","sourceState":"calendar-source-state.json","sourceStateSha256":"d27e7db96418dee59303b5583f81e4ecd0b6e3da1435cbb8e8ce8cfde00fc401"});
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
