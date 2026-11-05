(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9972c8138c5c3ab2.js","sha256":"9972c8138c5c3ab298d58393d129f3954b29e0e679fdb2dada63c60d7ccd8cdd","count":150});
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
