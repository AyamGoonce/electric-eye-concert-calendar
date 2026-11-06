(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e7257ae5d40b1541.js","sha256":"e7257ae5d40b154109d48fc28de01e27866c9365ac15854c131dd8a0589a13dc","count":150});
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
