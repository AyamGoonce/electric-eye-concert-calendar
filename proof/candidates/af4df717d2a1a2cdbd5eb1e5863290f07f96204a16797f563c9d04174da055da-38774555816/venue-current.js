(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2a1af5e8cf1d6a65.js","sha256":"2a1af5e8cf1d6a656527f501eb0230a7f6bc50905aa7cbbac308eff6645a1d8b","count":162});
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
