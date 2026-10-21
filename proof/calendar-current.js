(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.52fdf6aa8f4c3e74.js","sha256":"52fdf6aa8f4c3e7464785014741b3eb3f6d9e961c60520b06982685b52b43aa2","count":2066,"publishedAt":"2026-10-21T10:50:23Z","state":"calendar-state.json","stateSha256":"d0e55217d07455c04d1e2f3dee2bd5ca9a976921787f2cd2999d1d31871b1457","sourceState":"calendar-source-state.json","sourceStateSha256":"dd3a75302b82658ee9e32073469a9c0f353e2997151baf6ef1f8d0fe9a0cc73c"});
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
