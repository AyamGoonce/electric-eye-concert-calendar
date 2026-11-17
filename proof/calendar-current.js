(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9d068cf0fa3eeb7a.js","sha256":"9d068cf0fa3eeb7aecc83d0abb6a78e4dc8cbb5bb69cd862447d98885756e8a0","count":2121,"publishedAt":"2026-11-17T15:35:20Z","state":"calendar-state.json","stateSha256":"087af9222b9adc5277896c510823912d90872d41caec3369662990bcb62cca4b","sourceState":"calendar-source-state.json","sourceStateSha256":"4b1c385860d6e99bbdf9f8a3c471106a57e75e8173c74ed0c64b9c8d6cfd7c15"});
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
