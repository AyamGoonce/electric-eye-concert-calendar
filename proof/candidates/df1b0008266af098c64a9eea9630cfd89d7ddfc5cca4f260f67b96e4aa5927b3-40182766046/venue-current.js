(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1d3fb46e8baf8cec.js","sha256":"1d3fb46e8baf8cecbe1de88b63732fa91cc781404acc5165a5440c32a06577fb","count":154});
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
