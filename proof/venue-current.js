(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2ae085414eeab228.js","sha256":"2ae085414eeab2286aee93bcb2ec8df52fa5d858a936e166018152a17c77a95f","count":180});
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
