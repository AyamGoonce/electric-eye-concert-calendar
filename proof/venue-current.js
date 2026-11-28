(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.983a4efa3d6f55a5.js","sha256":"983a4efa3d6f55a5c9b5ae98f34a34f8bb8447cdc4068e21a429ad2446b8c501","count":181});
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
