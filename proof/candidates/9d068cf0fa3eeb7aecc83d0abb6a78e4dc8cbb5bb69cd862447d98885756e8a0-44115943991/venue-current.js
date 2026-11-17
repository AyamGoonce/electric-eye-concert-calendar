(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.848058c51b0d2178.js","sha256":"848058c51b0d217883ab1517c9013089103f0a8058adf935aca881dfbd9f3991","count":182});
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
