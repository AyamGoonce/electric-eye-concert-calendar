(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c8d1039f03701f83.js","sha256":"c8d1039f03701f83c4f391fee6f9a19f77a27207c7600a61b67de79774fe932c","count":150});
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
