(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.40033d2c5109b1bb.js","sha256":"40033d2c5109b1bbacfdc9672d49ed3e350ec27c3783489daa90d5c38320db68","count":156});
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
