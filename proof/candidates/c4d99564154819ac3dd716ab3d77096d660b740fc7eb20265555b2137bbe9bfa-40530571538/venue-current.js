(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1a97ffbd659a41b9.js","sha256":"1a97ffbd659a41b9ef5d0bad76b3d9b7f6d9276d303742e4dd7e06c19a045fe3","count":154});
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
