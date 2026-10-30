(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.680eab93e26cb0d1.js","sha256":"680eab93e26cb0d1305fb3cba0f02ee9927ae346f8eceef4881fc9b1f9943798","count":154});
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
