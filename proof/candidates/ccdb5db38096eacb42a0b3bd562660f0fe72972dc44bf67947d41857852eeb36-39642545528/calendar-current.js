(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ccdb5db38096eacb.js","sha256":"ccdb5db38096eacb42a0b3bd562660f0fe72972dc44bf67947d41857852eeb36","count":2073,"publishedAt":"2026-10-21T17:20:36Z","state":"calendar-state.json","stateSha256":"0e9e80ac77d81a40dd82cd335eb5318242b2c28601d46f486637bee5447dc687","sourceState":"calendar-source-state.json","sourceStateSha256":"b5ad1a04e8e3debe3dccfec2dae1dc0506b78fbd5b02eb5d9ff0c14353e0d6ae"});
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
