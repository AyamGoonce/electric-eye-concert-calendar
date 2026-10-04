(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.86f8fa0d898ced8a.js","sha256":"86f8fa0d898ced8ae7ca92b8b559740d9b12bd535d91835dc92ec3cdf438b312","count":168});
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
