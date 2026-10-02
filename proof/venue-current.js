(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b34c99fd3ba0868c.js","sha256":"b34c99fd3ba0868ccf50b153e33de3e21ac6a0d9d3a050f6f5aafc1072e488e4","count":109});
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
