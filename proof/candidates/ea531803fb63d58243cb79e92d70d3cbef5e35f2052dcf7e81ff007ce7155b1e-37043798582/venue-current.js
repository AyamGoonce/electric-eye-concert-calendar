(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.500594a9169ddbcc.js","sha256":"500594a9169ddbcc956a9de028a236560297c5afbf4c803f3af0b61ff12e5043","count":109});
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
