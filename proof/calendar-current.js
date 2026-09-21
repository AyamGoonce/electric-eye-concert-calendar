(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.38a745a3fdea47cc.js","sha256":"38a745a3fdea47ccda475b5c48559e0ab843564098503bc8e2ff2fc53d5195e3","count":2141,"publishedAt":"2026-09-21T12:25:32Z","state":"calendar-state.json","stateSha256":"bb46ef0e2d1e5feb9987be6b4d4638df5d0d3dcaf46011f4537af731e2ee7e15"});
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
