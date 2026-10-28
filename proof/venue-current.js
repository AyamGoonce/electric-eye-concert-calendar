(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f0d2f38a5b3bce18.js","sha256":"f0d2f38a5b3bce1885e12085b9a1dc519543a8fb9e992e5ba91d7553d333082d","count":155});
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
