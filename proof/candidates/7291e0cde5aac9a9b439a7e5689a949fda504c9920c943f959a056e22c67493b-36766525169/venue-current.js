(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.bb4f2b9ec793995e.js","sha256":"bb4f2b9ec793995ed124428fef84d59b7d4d0d0a2d3dd95c8f0ca57ad3788232","count":109});
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
