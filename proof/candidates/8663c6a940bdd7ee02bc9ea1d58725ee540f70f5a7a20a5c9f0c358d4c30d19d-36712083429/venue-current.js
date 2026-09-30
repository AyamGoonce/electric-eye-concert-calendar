(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ffdd125c2696349f.js","sha256":"ffdd125c2696349f56bbf5a557e77d1c68719c6ed20c8b854201e96d5188233b","count":109});
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
