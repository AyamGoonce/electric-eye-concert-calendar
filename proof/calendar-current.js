(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a6a3600ade1321de.js","sha256":"a6a3600ade1321dea68b18cfc092b5e12b9c2b1b5a3269ec4e10a8e647616f35","count":2104,"publishedAt":"2026-11-15T12:01:18Z","state":"calendar-state.json","stateSha256":"4336892d3c33029064192d307412ec5f2cda9c0c10c2185293ceea9cb1301d1c","sourceState":"calendar-source-state.json","sourceStateSha256":"fbe7e519f1a9f41ceaac4cac064ab8068c5952af3e331d50e4420fec4b38e95b"});
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
