(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6ec99d0d5f8c8bfd.js","sha256":"6ec99d0d5f8c8bfddebff9af3fec09ae60d8b3d14b1d23f821f1274d913d2361","count":154});
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
