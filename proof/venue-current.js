(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ba63c27ad3ff2c60.js","sha256":"ba63c27ad3ff2c6021eedfe22cd6fb1bc128876133252c543406880d6758bf7b","count":167});
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
