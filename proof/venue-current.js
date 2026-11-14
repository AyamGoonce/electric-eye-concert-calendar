(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1e685c018972d88b.js","sha256":"1e685c018972d88bc8b005feae88e5ec3dd8a452a9ff53bdf135921b08f1dc32","count":179});
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
