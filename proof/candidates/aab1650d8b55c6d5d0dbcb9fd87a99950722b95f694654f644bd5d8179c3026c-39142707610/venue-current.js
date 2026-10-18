(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.057e67431c8596e2.js","sha256":"057e67431c8596e2c5aba1be60adb61ce66acd0277b314e4b1715c704c31e048","count":154});
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
