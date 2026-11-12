(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9255c6336e78048a.js","sha256":"9255c6336e78048a2e2a236866868c2c3f5e51baf5168bd739a028f3d14a1ea0","count":2141,"publishedAt":"2026-11-12T00:48:15Z","state":"calendar-state.json","stateSha256":"c8d4a2831ad9380e141303239f1fdc734d9b4e0592988e5b9f6a9172b8d2a63d","sourceState":"calendar-source-state.json","sourceStateSha256":"7bed04002a240c05c2d094c30ff99a7f30f6cec10378322891c766830129e87c"});
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
