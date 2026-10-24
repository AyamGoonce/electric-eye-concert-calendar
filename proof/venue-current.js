(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.21e9d43f6c1470bd.js","sha256":"21e9d43f6c1470bd77459a1e6405a4b263d0cfaa86636f0d9c7fb764a9e23f18","count":155});
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
