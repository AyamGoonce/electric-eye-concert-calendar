(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9d3b990b643bccea.js","sha256":"9d3b990b643bccea2e4e05e3239947f95716458d4729c803cfed1a9d3f828eaf","count":179});
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
