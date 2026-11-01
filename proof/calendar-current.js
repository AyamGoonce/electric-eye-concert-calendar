(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cea121226576a9df.js","sha256":"cea121226576a9dfb5dcdc9b478a163ee86f98218c1a60771bfaec31c1b3ed8f","count":2027,"publishedAt":"2026-11-01T19:46:38Z","state":"calendar-state.json","stateSha256":"bcf7af84049766e454ef7f9ee3c81e9046694be45445a8d946b3c794349fd4f0","sourceState":"calendar-source-state.json","sourceStateSha256":"6b397dfb434aeb89505e026db30f98c01616779185a70c8af77f9e178ec0cf6d"});
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
