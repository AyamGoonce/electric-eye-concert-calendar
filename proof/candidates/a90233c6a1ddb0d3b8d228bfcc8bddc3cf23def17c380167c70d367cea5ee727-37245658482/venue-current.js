(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b85b58c12fe2a693.js","sha256":"b85b58c12fe2a693413595818cd7d189f04b721e1b79fa7cbc1fc8cb902bc328","count":160});
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
