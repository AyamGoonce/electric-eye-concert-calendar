(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.64ee2a0a379c0b87.js","sha256":"64ee2a0a379c0b8775e84fdab2246a0b7774ab55416143708c69fcccda3c5b91","count":109});
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
