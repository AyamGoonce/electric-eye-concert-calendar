(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.bd2de2612d698a39.js","sha256":"bd2de2612d698a39d90e2c571ed64a97a849be5f9827b3ecf6c3f358bd8214b6","count":109});
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
