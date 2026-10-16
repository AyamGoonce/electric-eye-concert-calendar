(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.08e70b574a2afd4c.js","sha256":"08e70b574a2afd4c1f5bb91a8dda0cb1744c4db37d0671c63f967bcf4d181113","count":156});
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
