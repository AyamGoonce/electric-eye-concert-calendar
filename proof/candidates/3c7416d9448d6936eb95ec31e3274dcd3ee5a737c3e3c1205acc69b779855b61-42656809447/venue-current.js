(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.fc4a0f463fafb1b0.js","sha256":"fc4a0f463fafb1b006d85a8cea5d8b79afe89f6ccc769f87c943cb3777ccefbc","count":180});
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
