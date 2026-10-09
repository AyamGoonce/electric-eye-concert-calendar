(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f7bb4f270b897c26.js","sha256":"f7bb4f270b897c263f443bd259d499e886d2579a64b90f7c96e2eeeda48bea76","count":168});
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
