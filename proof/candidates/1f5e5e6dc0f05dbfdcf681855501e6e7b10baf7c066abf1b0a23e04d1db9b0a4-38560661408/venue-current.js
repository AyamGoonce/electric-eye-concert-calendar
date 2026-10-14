(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.4c8a7bb25bc7bd34.js","sha256":"4c8a7bb25bc7bd3483c8b7aaa6b0685504907b3402bae3f3b2f0382e081d4476","count":164});
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
