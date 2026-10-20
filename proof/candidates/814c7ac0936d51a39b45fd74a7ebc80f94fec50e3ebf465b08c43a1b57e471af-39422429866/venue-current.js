(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9189786a32213f2e.js","sha256":"9189786a32213f2e5b142afd2e7380aa29c10e7c82c861404080766bf50da56e","count":156});
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
