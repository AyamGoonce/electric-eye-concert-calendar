(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.cc85e7d57dec7c1e.js","sha256":"cc85e7d57dec7c1e6b613aae50a138e24c79c3cadc31cf4eea0c91f5bd91aaa0","count":164});
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
