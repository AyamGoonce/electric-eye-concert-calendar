(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2a7c7342fc2f6568.js","sha256":"2a7c7342fc2f6568ef859aab8bc285e167b3b79d9db812d380e01d6c1d797327","count":154});
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
