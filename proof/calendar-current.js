(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.83199fc8230121fb.js","sha256":"83199fc8230121fb9492d2d075a01de88a4fd6955108640043ad75f1ed9d4810","count":2019,"publishedAt":"2026-11-02T00:50:46Z","state":"calendar-state.json","stateSha256":"2ae0faa1dd9a4c11963befbe14f317ed5962f4fdc2f5e4874e38e35392e7af3d","sourceState":"calendar-source-state.json","sourceStateSha256":"65235a1561c09975bfcdf1dcacc7fac0a92dda41a2849baee5b73555433a5124"});
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
