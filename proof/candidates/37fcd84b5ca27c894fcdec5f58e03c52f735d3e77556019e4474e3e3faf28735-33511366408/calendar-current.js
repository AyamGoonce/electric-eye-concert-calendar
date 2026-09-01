(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.37fcd84b5ca27c89.js","sha256":"37fcd84b5ca27c894fcdec5f58e03c52f735d3e77556019e4474e3e3faf28735","count":2263,"publishedAt":"2026-09-01T13:15:20Z","state":"calendar-state.json","stateSha256":"17a70f0ec582cd668b28d4e78a8b5ddb05547275034c458b2a47b0e61a4b69b6"});
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
