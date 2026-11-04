(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.fdf16ee5c2ec7b81.js","sha256":"fdf16ee5c2ec7b815d44f1c5d3b9b24c0ec8e3ff50df36713e5382a8bb72fb4d","count":152});
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
