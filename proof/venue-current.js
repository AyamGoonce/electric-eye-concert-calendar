(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d3f5281a21ece877.js","sha256":"d3f5281a21ece877115f2afe8689e3edf69222ae7142c17e55be3ab50bb2c389","count":109});
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
