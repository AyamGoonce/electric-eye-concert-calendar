(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.95195644c7f0c764.js","sha256":"95195644c7f0c764234541c6ed3de57f6328daf8a93f90340c13a7784caeb8e3","count":177});
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
