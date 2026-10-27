(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0cc7f33777d10fc8.js","sha256":"0cc7f33777d10fc82e6bccd4eea27ff59ade3e3db55c8515dea844ad05b9c167","count":154});
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
