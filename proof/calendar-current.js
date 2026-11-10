(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.623f182eebb57e75.js","sha256":"623f182eebb57e75bdf912359095d3517199ffec9ad061c0b23face7a6a3a56c","count":2204,"publishedAt":"2026-11-10T12:25:56Z","state":"calendar-state.json","stateSha256":"29a445f340e7ab2a551878db0a7fb70c0badbc86093e0480822dcc66cf6b23cb","sourceState":"calendar-source-state.json","sourceStateSha256":"989e3b4ead2faac73d8e74982862763da31c9eba30e62b9e85533e0348a2481b"});
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
