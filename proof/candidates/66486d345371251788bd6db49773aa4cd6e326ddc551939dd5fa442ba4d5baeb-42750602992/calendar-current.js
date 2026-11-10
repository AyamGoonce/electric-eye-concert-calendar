(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.66486d3453712517.js","sha256":"66486d345371251788bd6db49773aa4cd6e326ddc551939dd5fa442ba4d5baeb","count":2193,"publishedAt":"2026-11-10T03:37:20Z","state":"calendar-state.json","stateSha256":"5fe5b50fcf61f3bd9e1530fde6a8bf314f259c30ec06c08b655d9edf4ba6695c","sourceState":"calendar-source-state.json","sourceStateSha256":"aa7b995426e8e8f8d29f9fbb53149fa8f77d5347afbed2290987cef303826fb0"});
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
