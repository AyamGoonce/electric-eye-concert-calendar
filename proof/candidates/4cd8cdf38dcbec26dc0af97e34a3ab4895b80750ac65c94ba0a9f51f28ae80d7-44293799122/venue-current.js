(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0e279c93714ac4cd.js","sha256":"0e279c93714ac4cd4c66f0217ef04065d4a1f596cb04c7d517e0b8eb816d3c6f","count":179});
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
