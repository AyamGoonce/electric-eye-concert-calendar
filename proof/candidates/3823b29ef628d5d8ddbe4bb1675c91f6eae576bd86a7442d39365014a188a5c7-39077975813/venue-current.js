(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1d37f5361f8988ce.js","sha256":"1d37f5361f8988ce695650c6875db69e60bbdf610948dc6ed669ac7817334f11","count":155});
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
