(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1b99b0cf9746e273.js","sha256":"1b99b0cf9746e2734a20c07cabd85304271991f6085a9349bc59ac6fd5a32f14","count":152});
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
