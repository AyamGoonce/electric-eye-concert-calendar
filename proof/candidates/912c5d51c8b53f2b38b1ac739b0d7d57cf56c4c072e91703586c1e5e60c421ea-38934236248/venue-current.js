(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0300b195785c3b52.js","sha256":"0300b195785c3b52a61be21b827e37b0028e8f9f8bbabb1075e0543971ad970e","count":159});
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
