(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5ff83fa6f5f34a37.js","sha256":"5ff83fa6f5f34a37df3efcf3a3b19a175265c5dff6bbaec8ce273814af0743eb","count":154});
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
