(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.21cf74ba8b7efa4f.js","sha256":"21cf74ba8b7efa4f75a0814d1063f87cadd94c056ba383aabcbd02093949e918","count":149});
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
