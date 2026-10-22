(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a73a27077336a8a8.js","sha256":"a73a27077336a8a8dc0968a805bd87912c8c04dc89bb63e4c07dd1c5f0072973","count":156});
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
