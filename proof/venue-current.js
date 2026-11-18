(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0c5dfcc2047a917e.js","sha256":"0c5dfcc2047a917eae861ddb9f98c7455667d8d816b858b8bbc3841e4311f7fa","count":180});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
