(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f9a9ef9af6556d9e.js","sha256":"f9a9ef9af6556d9ed8306eda89b219f71df762fc38cc28f2d96fedd497633715","count":177});
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
