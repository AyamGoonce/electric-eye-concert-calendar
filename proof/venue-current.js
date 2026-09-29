(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9208f13c73d01a44.js","sha256":"9208f13c73d01a446522611f95681f9e16b2bb84b6fd9bebe7da5684fc6cd23b","count":109});
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
